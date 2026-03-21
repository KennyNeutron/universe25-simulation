from agents.agent import Agent
from config import AGENT_COUNT


class Simulation:
    """Manages the collection of agents and drives the simulation loop."""

    def __init__(self):
        self.agents: list[Agent] = [Agent() for _ in range(AGENT_COUNT)]

    def update(self, dt: float) -> None:
        """Update every agent by one time-step.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        for agent in self.agents:
            agent.update(dt)
