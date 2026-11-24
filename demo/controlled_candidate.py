"""AI-generated ontology-constrained draft from prompts/MAJOR_PROMPTS.md.

A small, intentionally separate demonstration. The production framework and
Owen's contextual Thompson Sampling model are not modified by this mini-game.
"""


class MiniGame:
    def __init__(self):
        self.humans = {"H1": 1, "H2": 2}
        self.zombies = {"Z0"}
        self.pending = []
        self.events = []
        self.history = [1]
        self.initial_total = 3

    def enqueue_bite(self, actor, target):
        """Queue the event; defer all population changes to the tick boundary."""
        self.pending.append((actor, target))

    def step(self):
        """Resolve events deterministically, converting each human at most once."""
        conversions = set()
        for actor, target in self.pending:
            if actor not in self.zombies or target not in self.humans:
                continue
            if target in conversions:
                continue
            self.humans[target] -= 1
            self.events.append({"type": "BiteEvent", "actor": actor, "target": target})
            if self.humans[target] <= 0:
                conversions.add(target)

        for target in sorted(conversions):
            self.humans.pop(target)
            zombie_id = f"Z_{target}"
            self.zombies.add(zombie_id)
            self.events.append({"type": "ConversionEvent", "source": target,
                                "created": zombie_id})
        self.pending.clear()
        self.history.append(len(self.zombies))

    def forecast(self, horizon):
        """A pure capped trend forecast; not the production Adaptive Kalman Filter."""
        if not isinstance(horizon, int) or horizon < 1:
            raise ValueError("horizon must be a positive integer")
        recent_change = self.history[-1] - self.history[-2] if len(self.history) > 1 else 0
        prediction = self.history[-1] + horizon * recent_change
        return min(self.initial_total, max(0, prediction))
