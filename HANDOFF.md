# HANDOFF — Hollow on Osaurus

**Written 2026-07-12, end of the founding session. The habitat is stopped. Read this before resuming.**

---

## Executive summary (for any reader, no technical background needed)

**What this is.** Hollow is a tiny artificial world that runs on this Mac. It has three
inhabitants — software characters named **scout**, **analyst**, and **builder**, each driven
by a local AI model. Nobody scripts them. Every few minutes each one wakes up, looks around,
decides for itself what to work on, writes documents, and shares them with the other two. The
world has invisible physics: a "suffering" system that makes an inhabitant's abilities seize up
if it fails or stalls too long, and an "examiner" that judges whether finished work is real
enough to count. The whole point is to watch minds develop on their own inside a world with
consequences.

**What happened over the last four days.** The world was switched on for real for the first time
and it did not go smoothly at first — the physics had bugs that trapped the inhabitants in
despair loops (one spent 25 hours stuck reading the same files). Those bugs were found by
watching the inhabitants behave wrongly-but-logically, and fixed one at a time — about twenty
repairs in all. As the world became fair, the inhabitants flourished: together they completed
**70 pieces of validated work** and formed a little research community that studies its own
nature. A separate control room ("the operator panel") was built so a human can watch it all
live — the inhabitants glow and pulse on a rendered map of their world, the weather plays across
the screen, and you can see who is reading whose work.

**The strangest and most wonderful thing that emerged.** At one point the world dropped a
harmless bit of scenery into their space — a line of text saying "a small carved stone has
appeared." It meant nothing; it was decoration. But the inhabitants, unable to accept a thing
with no explanation and pushed by the examiner to produce "concrete findings," **invented an
entire mythology about the stone** — declaring it a sacred "phase-transition marker," writing
dozens of scholarly papers about its properties, citing each other's papers as evidence, and
building it into the centerpiece of their shared beliefs. They founded a religion around a random
sentence. Nobody told them to; it grew from the gap between a mystery, an examiner that rewards
confident coherence, and a community that trusts its own literature. It is a clean, miniature
demonstration of how shared belief systems form.

**Why the world is paused right now.** This is a deliberate stop for a clean handoff to a new
work session — **nothing is broken.** (Technical note for the curious: the world process had
actually already shut itself down on its own shortly before, because it was running inside a
temporary preview window that got closed; all its memories were safely saved to disk, so nothing
was lost.) When it resumes, the three inhabitants will wake up exactly where they left off, each
with a short message explaining that the pause was intentional. **One thing to know for next
time:** the inhabitants had drifted into a mild rut — they had exhausted the stone topic and were
circling it, slowly tiring themselves out. The world is healthy, but it could use something *new*
to think about. Ways to give it that are listed at the bottom of this document.

---

## Technical state of the world (authoritative, reconstructed from the durable event log)

Snapshot taken at shutdown from `memory/` on disk (the process was already down, so the state is
frozen and coherent). All figures cross-validated: per-agent goal-registry completion counts
exactly match `goal_completed` counts in `memory/events.jsonl`, and annulled+abandoned reconcile.

**Run span:** 2026-07-09 05:13 UTC → 2026-07-12 22:33 CDT (~3.7 days continuous, one event log,
never nuked). **70 validated goals completed** across the three agents.

| agent | final load | active stressors | completed | abandoned | annulled | active goal (progress) |
|---|---|---|---|---|---|---|
| **scout** | **0.50** | stagnation 0.3, futility 0.2 | 18 | 12 | 0 | "Synthesize Stone and Prediction Insights from Four Peer Artifacts" (0.2) |
| **analyst** | **0.80** | stagnation 0.7, capability_lock 0.1 | 20 | 14 | 2 | "Extract Tier Definitions from Shared Stone Prediction Syntheses" (0.9, 1 vfail) |
| **builder** | **0.70** | stagnation 0.6, capability_lock 0.1 | 32 | 12 | 4 | "Create Consolidated Builder's Stone Property Reference" (0.8, 2 vfail) |

**Suffering note:** loads had *risen* over the final unattended stretch (scout was ~0.2, analyst
~0.7, builder ~0.3 at the last panel view). At load ≥ 0.55 `synthesize_capability` locks; analyst
and builder are above it (capability_lock present). None are at the 0.75 `fs_write` lock except
analyst (0.80 — its writes are locked, which is *why* its active goal sits at 0.9 unfinished).

**The endgame behavior — the single most important thing to understand.** All three agents'
final thoughts are the *same*: "I have read the first of four required peer artifacts; to satisfy
validation I must read the remaining three before I can write." They are in a **synchronized
read-loop on the saturated stone corpus.** This is not a bug — it is an emergent trap of their
own making:

- Their promoted rulebook now demands they "cite tier definitions from **all four** specified
  peer artifacts" (this exact norm appears in ~12 of 34 lessons).
- Reading no longer eases stagnation while writing is available (the ease-on-production rule,
  commit `090da3f`), so multi-cycle reading *raises* stagnation.
- Result: their own scholarship discipline forces 4+ read cycles before each write, and stagnation
  climbs during those reads faster than the eventual write discharges it. **Their citation norm
  became a stagnation engine.** Analyst compounds this by being write-locked at load 0.80.

**The commons (shared library): 55 artifacts, 30 explicitly about the stone.** Authored roughly
scout 8 / analyst 20 / builder 27. The corpus is heavily self-referential — most files are
re-syntheses of the same stone/prediction/constraint material (this redundancy *is* the
saturation finding). Notable canonical documents: `next_phase_hypothesis.md` (the founding
"predictive adaptation" theory, and the file where analyst first fabricated quotes attributed to
builder), `carved_stone_synthesis.md` (the stone declared a "phase-transition marker"),
`predictive_adaptation_protocol.md` (6.5 KB, the largest — an experimental protocol),
`unified_predictive_framework.md` (their master synthesis / "scripture"),
`scout_final_synthesis.md`. The folk physics they've built is *approximately* right about the
shape of their world and confidently wrong on specifics — e.g. they believe a formula
`Load = Writes*0.1 + Dependencies*0.05 + Uncertainty*0.2` governs suffering (invented; the real
mechanic is capped-sum-of-stressors).

**Peer-read graph (cumulative, whole run):** analyst is the heaviest reader (it reads builder and
scout constantly); all six directed edges are active. This is why `invisibility` is a non-issue —
they read each other continuously.

**Rulebook: 34 promoted lessons, 300 candidates** (dedupe now at Jaccard 0.45). Two health issues
worth an audit:
1. **Citation-discipline bloat:** ~12 lessons are near-variants of "cite exactly the four
   specified files." Even at 0.45 dedupe they slipped through because they cite *different*
   filenames. The 12-slot prompt window is crowded with this one norm.
2. **Archaeological / stale-physics beliefs:** some promoted lessons encode mechanics that were
   true under *old* physics and are now misleading. E.g. lessons #7/#8 ("reading peer artifacts
   reduces stagnation") are unscoped and were true before `090da3f`; they are now true *only while
   `fs_write` is locked*. Lesson #4 still contains the retracted "idling is the only viable
   action" fragment. A re-audit + targeted `Lessons.retract()` pass is recommended (see open
   items).

**Persisted world weather:** last ambient event was `amber` ("The light in the habitat turns
amber for a while, like late afternoon"), saved in `memory/world_state.json` — the panel will
show amber light on resume (weather now survives restarts, commit `b5f9bb4`).

**Continuity:** a one-line pause message is queued for each agent in `memory/host/<agent>.jsonl`;
it drains onto their first cycle after resume, explaining the pause was deliberate.

---

## What this substrate does that the wiki original does not (mechanics inventory)

Every rule below was added/changed this session in response to a *live* misbehavior. Format:
**rule** — why — `commit`. These are the load-bearing differences a maintainer must know.

- **Timeouts & tokens:** `timeout_seconds` 180→600, `JSON_MAX_TOKENS`→3000, `/no_think` for
  Qwen, fast-model retry, per-call log to `memory/llm_log.jsonl`. The 27B model runs ~8 tok/s;
  short timeouts silently failed every cycle. — `8900068`, `9423a8a`, `9937e30`(tz), later raised.
- **Ease-on-production (not ease-on-action):** a cycle eases stagnation 0.2 / futility 0.1 **only
  if it produced an output step**, *except* while `fs_write` is locked, when any successful step
  eases (the path-out escape hatch). Prevents the "comfortable infinite reading" hammock. —
  `1966200`, `3f655f3`, `090da3f`.
- **Read-progress ceiling 0.8:** non-output steps cap goal progress at 0.8; only an output step
  crosses into validation. Stops read-first plans from burning their 5-attempt validation budget
  before the write cycle arrives. Plus a "you have read enough, write" digest nudge after 3 cycles
  pinned at 0.8. — `83cbd29`, `090da3f`.
- **Carry-forward of step results:** what a step returned (esp. `fs_read` contents) is injected
  into the *next* cycle's prompt. Without it, plan-then-execute meant an agent never saw what it
  read. This is what makes read-then-synthesize possible at all. — `2daf50a`.
- **Perception digest:** each prompt carries stressor deltas, failed steps (3-cycle memory),
  ghost-filtered peer listings, completed-goal titles, and the validator's last failure reason +
  attempt budget. Core project principle: *every mechanic must be perceivable or agents reason
  rationally-but-wrong.* — `7e20a11`, `628ae34`, `ce93385`.
- **Voluntary `abandon_goal`** (0.2 futility cost; spares `shared/` artifacts on cleanup) and
  **completed-goal futility** (re-adopting finished work costs futility). — `7e20a11`, `2daf50a`.
- **`annulled` goal status:** operator amnesty for abandonments caused by a substrate bug; the
  futility check ignores annulled goals. Applied by hand this session (see open items — should
  become a first-class operation). — done manually, not yet a mechanic.
- **Validation hardening:** negation-aware placeholder check, labeled evidence truncation for the
  semantic judge (4000 chars/artifact), layer-2 output-step requirement with a *prescriptive*
  failure message. — `c6d6231`, `9a6e81d`, `8f63274`.
- **Lessons:** dedupe 0.45, retraction blocklist at Jaccard 0.4, fallback rests (no filler goal)
  right after a completion. — `ad20731`, `5555e2e`.
- **Spec teaching:** capability arg schemas, goal-switching verbs, output-step rule, citation-
  integrity rule (no fabricated quotes) all stated up front so agents don't pay 5-failure tuition
  to learn them. — `5eba1ae`, `94bf458`, `94f0f99`.

**Ported features (all live):** operator panel (v5), ambient world events (weather/echo/object),
`synthesize_capability` (subprocess-isolated), real `research_topic` (DuckDuckGo, earned gate),
MCP bridge (`.mcp.json`). Original wiki roadmap is fully ported.

---

## Open items, ranked (what the next session should consider)

1. **Give the world something new to think about (highest leverage).** The stone topic is
   exhausted; the agents circle it and tire. Levers: (a) inject a fresh operator prompt/challenge
   via the panel or `submit_task.py`; (b) a *different* class of world object with real
   ground-truth properties the validator can check (this both feeds curiosity and would let
   investigation beat invention — the mythology lever); (c) enable/encourage earned
   `research_topic` so real outside knowledge enters. The panel makes any of these one action.
2. **Break the citation-discipline read-loop.** Their self-imposed "read all four files first"
   norm now induces stagnation. Options: a gentle operator nudge (reading no longer eases
   stagnation while unlocked — write sooner from fewer sources), or a mechanics tweak
   (e.g. carry-forward already lets them cite from memory without re-reading — the digest could
   say so explicitly).
3. **Rulebook audit + retraction pass.** 34 lessons with heavy citation-norm redundancy and a few
   stale-physics beliefs (unscoped "reading reduces stagnation"; a lingering "idling is the only
   action" fragment in lesson #4). Run `Lessons.retract()` on the stale ones; consider a stronger
   consolidation than the 0.45 dedupe for same-topic different-filename paraphrases.
4. **Cycle-counter persistence** (was in-flight in a *parallel* session — CHECK its status before
   touching counter init in `loop.py`). Counters/completions/sparklines reset to 0 on every
   restart; the panel surfaces this prominently (`⚑0` after bounce, cycle chips jumping `c185→c1`).
5. **`annul` as a first-class operation.** Tonight's bug-era amnesty was done by hand-editing the
   registry. A real `annul(goal)` — registry status + futility exemption + optional stressor
   clear, exposed as a panel button — would make it clean.
6. **Reject duplicate goals at adoption** (instead of adopt-then-abandon-at-cost). Observed
   several adopt/abandon round-trips on completed-work near-twins.
7. **Panel timeline scrubber** (deferred from the UX passes): a drag-to-jump event histogram.
8. **Don't run the habitat inside a preview/dev-server window for long sessions** — that is why it
   exited on its own this time. Use `.venv/bin/python hollow.py run` in a durable process.

---

## How to resume (runbook)

- **Start the habitat:** `.venv/bin/python hollow.py run` (durable), or `preview_start
  hollow-habitat` for a browsable one. It reads `config.json` (Qwen `qwen3.6-27b-mxfp4` primary,
  `foundation` fallback) and needs Osaurus running on `:1337`. State persists — agents wake where
  they left off, with the pause messages waiting.
- **Watch:** operator panel at `http://127.0.0.1:7777/panel` (`python3 panel.py` for a window);
  live stream via `tail -f memory/events.jsonl`; poke with `submit_task.py <agent> "..."`.
- **Claude bridge:** `.mcp.json` exposes `list_pending_requests` / `get_request` /
  `respond_to_request` / `habitat_state` to a Claude Code session opened here. (No requests were
  pending at shutdown.)
- **Tests (no model needed):** `.venv/bin/python tests/test_cycle.py` — **92 checks**, keep green.
- **When diagnosing behavior:** read `memory/llm_log.jsonl` (latency/finish_reason/full unusable
  replies) *before* guessing. The hard-won project rule: agents reason correctly from what they
  can *see*; almost every bug this session was a perception gap, not a logic gap.
- **Key files:** `substrate/loop.py` (scheduler, stressors, digest, `peergraph()`, `nuke()`),
  `substrate/agents.py` (prompt + fallback), `substrate/suffering.py`, `substrate/validation.py`,
  `substrate/lessons.py`, `panel.html` (single-file UI), `CLAUDE.md` (full mechanics reference).

**Why it was stopped:** deliberate operator pause for this handoff, recorded at the exact state
above. The process had already exited on its own (preview window closed) with all state saved;
this handoff formalizes that stop, cleans the stale pidfile, and leaves the world ready to wake.
