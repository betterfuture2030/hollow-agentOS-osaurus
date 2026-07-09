"""Hollow-on-Osaurus substrate.

A Mac-native rebuild of the Hollow AgentOS substrate that talks to an
OpenAI-compatible local model server (Osaurus) instead of Ollama.
"""

import json
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

AGENT_NAMES = ("scout", "analyst", "builder")

DEFAULT_CONFIG = {
    "osaurus": {
        "base_url": "http://127.0.0.1:1337/v1",
        "default_model": "",
        "fallback_model": "",
        # generous: a 27B-class model on consumer silicon runs ~8 tok/s, so a
        # full JSON_MAX_TOKENS plan can take ~6 minutes; sized to match llm.py
        "timeout_seconds": 600,
    },
    "runtime": {
        "cycle_interval_seconds": 20,
        "api_port": 7777,
        "max_steps_per_cycle": 2,
    },
    "world": {
        # one ambient event (weather/echo/object) every N scheduler rounds;
        # 0 disables the world. seed fixes the sequence (tests use this).
        "event_every_rounds": 6,
        "seed": None,
    },
    "research": {
        # research_topic performs a real web search (the habitat's only
        # outbound network call). Set false to keep the habitat fully local.
        "enabled": True,
    },
}


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    for section, values in cfg.items():
        merged.setdefault(section, {})
        if isinstance(values, dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged


def save_config(path: Path, cfg: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
