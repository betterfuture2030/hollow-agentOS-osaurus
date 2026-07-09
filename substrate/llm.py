"""OpenAI-compatible client for Osaurus (or any local /v1 server)."""

import json
import re
import threading
import time
from datetime import datetime

import httpx


class LLMError(Exception):
    pass


THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)

# json_chat generates less than free-form chat: a plan is a few hundred
# tokens, and on a ~8 tok/s local model every 1000 tokens is ~2 minutes.
# But a plan's fs_write step carries full document content, and tight caps
# were observed truncating artifacts mid-sentence (validation then rejects
# them as incomplete) and squeezing thoughts. 3000 tokens ≈ 6 min worst-case
# generation — the 600 s timeout is sized to match. Lowering this trades
# artifact/thought completeness for latency; history says don't.
JSON_MAX_TOKENS = 3000
# Qwen3-family soft switch: appending this to the system prompt suppresses
# <think> blocks, which we strip anyway. Ignored by other models.
NO_THINK_MARKER = "/no_think"
NO_THINK_MODEL_SUBSTRINGS = ("qwen",)
# Kept when logging an unusable reply for offline prompt iteration.
# JSON_MAX_TOKENS bounds replies to a few KB, so keep effectively all of it:
# diagnosing a parse failure needs the tail, not the head.
FAILURE_SNIPPET_CHARS = 8000


def strip_thinking(text: str) -> str:
    """Qwen3-family models emit <think>...</think> blocks; drop them."""
    return THINK_RE.sub("", text).strip()


def extract_json(text: str):
    """Best-effort extraction of the first JSON object in a model reply."""
    text = strip_thinking(text)
    fenced = FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


class OsaurusClient:
    """Thin chat-completions client. All calls are serialized through one
    lock: a 24 GB machine runs one loaded MLX model, and concurrent
    inference requests just thrash it."""

    def __init__(self, base_url, default_model, fallback_model="", timeout=180, log_path=None):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.fallback_model = fallback_model
        self.timeout = timeout
        self.log_path = log_path
        self._lock = threading.Lock()

    def _log(self, record: dict) -> None:
        """Append one call record to the llm log; never let logging fail a call."""
        if not self.log_path:
            return
        record = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"), **record}
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def health(self) -> bool:
        try:
            r = httpx.get(f"{self.base_url}/models", timeout=5)
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def list_models(self):
        r = httpx.get(f"{self.base_url}/models", timeout=10)
        r.raise_for_status()
        return [m["id"] for m in r.json().get("data", [])]

    def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> str:
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        record = {
            "model": payload["model"],
            "prompt_chars": sum(len(m.get("content") or "") for m in messages),
            "max_tokens": max_tokens,
        }
        started = time.monotonic()
        with self._lock:
            try:
                r = httpx.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=self.timeout,
                )
                r.raise_for_status()
            except httpx.HTTPError as e:
                status = "timeout" if isinstance(e, httpx.TimeoutException) else "http_error"
                self._log({**record, "status": status, "ms": int((time.monotonic() - started) * 1000), "error": str(e)[:200]})
                raise LLMError(f"chat completion failed: {e}") from e
        record["ms"] = int((time.monotonic() - started) * 1000)
        try:
            body = r.json()
            choice = body["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            self._log({**record, "status": "malformed_response"})
            raise LLMError(f"malformed completion response: {e}") from e
        self._log(
            {
                **record,
                "status": "ok",
                "finish_reason": choice.get("finish_reason"),
                "completion_tokens": (body.get("usage") or {}).get("completion_tokens"),
            }
        )
        return strip_thinking(content or "")

    def json_chat(self, system, user, model=None, temperature=0.3):
        """Chat expecting a JSON object back. One retry with a terser
        reminder, then None — callers must have a grounded fallback.
        Deliberately avoids response_format: MLX servers vary in support.
        A transport failure (timeout, connection) retries once on the
        fallback model, which is expected to be small and fast."""
        active_model = model or self.default_model
        if any(s in active_model.lower() for s in NO_THINK_MODEL_SUBSTRINGS):
            system = f"{system}\n{NO_THINK_MARKER}"
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        for attempt in range(2):
            try:
                reply = self.chat(
                    messages, model=active_model, temperature=temperature,
                    max_tokens=JSON_MAX_TOKENS,
                )
            except LLMError:
                if self.fallback_model and active_model != self.fallback_model:
                    active_model = self.fallback_model
                    continue
                return None
            obj = extract_json(reply)
            if obj is not None:
                return obj
            self._log(
                {
                    "model": active_model,
                    "status": "unusable_json",
                    "attempt": attempt,
                    "reply_snippet": reply[:FAILURE_SNIPPET_CHARS],
                }
            )
            messages.append({"role": "assistant", "content": reply[:2000]})
            messages.append(
                {
                    "role": "user",
                    "content": "That was not valid JSON. Reply with ONLY the JSON object, no prose, no code fences.",
                }
            )
        return None
