"""AI-generated naive draft from the short prompt in prompts/MAJOR_PROMPTS.md.

Demonstration only: this is intentionally retained UNFIXED so the same
independent acceptance gates expose whether the draft meets the requirements.
Do not import it into the production Zombie Game.
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
        self.pending.append((actor, target))

    def step(self):
        conversions = []
        for actor, target in self.pending:
            if target in self.humans:
                self.humans[target] -= 1
                self.events.append({"type": "BiteEvent", "actor": actor, "target": target})
                if self.humans[target] <= 0:
                    conversions.append(target)

        for target in conversions:
            self.humans.pop(target, None)
            zombie_id = f"Z_{target}_{len(self.zombies)}"
            self.zombies.add(zombie_id)
            self.events.append({"type": "ConversionEvent", "source": target,
                                "created": zombie_id})
        self.pending.clear()
        self.history.append(len(self.zombies))

    def forecast(self, horizon):
        if horizon < 1:
            raise ValueError("horizon must be positive")
        recent_change = self.history[-1] - self.history[-2] if len(self.history) > 1 else 0
        return max(0, self.history[-1] + horizon * recent_change)
