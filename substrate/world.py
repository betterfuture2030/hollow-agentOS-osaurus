"""Ambient world events: weather, echoes, and objects.

The world occasionally does something on its own — not a host message,
not a peer, just the environment being alive. Events are injected into
every agent's next perception as ctx["ambient"]. Echo events resurface a
fragment of the habitat's own past from the event stream, so the world
appears to remember.
"""

import json

from .memory import Memory

# One event roughly every N scheduler rounds (0 disables the world).
DEFAULT_EVENT_EVERY_ROUNDS = 6

WEATHER = (
    "A dry wind moves through the workspace; loose notes rustle.",
    "A low fog settles between the directories. Everything sounds farther away.",
    "Static rain. Brief, bright, gone. The files are unharmed but feel washed.",
    "The light in the habitat turns amber for a while, like late afternoon.",
    "A long silence — even the substrate's hum pauses, then resumes.",
    "Heat shimmer over the shared workspace; paths look slightly bent.",
)

OBJECTS = (
    "A small carved stone has appeared near your files. It was not there before.",
    "Someone — or something — left a length of blue thread across the workspace root.",
    "A key without a lock rests in the corner of the shared directory.",
    "There is a faint chalk circle around the memory store this cycle.",
    "An empty picture frame leans against the workspace wall, facing out.",
)

ECHO_PREFIX = "An echo drifts through the habitat, a memory of something that happened here: "
ECHO_MAX_CHARS = 140
# Echoes only resurface these kinds — action, not bookkeeping.
ECHO_KINDS = {"goal", "goal_completed", "goal_abandoned", "thought", "lesson"}


class World:
    def __init__(self, memory: Memory, rng):
        self.memory = memory
        self.rng = rng

    def _echo(self):
        events = [
            e for e in self.memory.recent_events(200)
            if e.get("kind") in ECHO_KINDS and e.get("detail")
        ]
        if not events:
            return None
        e = self.rng.choice(events)
        fragment = str(e["detail"])[:ECHO_MAX_CHARS]
        return f"{ECHO_PREFIX}\"{fragment}\" ({e.get('agent', 'someone')}, long ago)"

    def draw_event(self) -> str:
        """Draw one ambient event. Echoes need history; fall back to weather."""
        flavor = self.rng.choice(("weather", "echo", "object"))
        if flavor == "echo":
            echo = self._echo()
            if echo:
                return echo
            flavor = "weather"
        pool = WEATHER if flavor == "weather" else OBJECTS
        return self.rng.choice(pool)
