from agents.agent import Agent
from environment.food import Food
from config import AGENT_COUNT, FOOD_COUNT


class Simulation:
    """Manages agents and food, and drives the simulation loop."""

    def __init__(self):
        self.agents: list[Agent] = [Agent() for _ in range(AGENT_COUNT)]
        self.foods: list[Food] = [Food() for _ in range(FOOD_COUNT)]

    def update(self, dt: float) -> None:
        """Update every agent and handle eating / food respawn.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        for agent in self.agents:
            agent.update(dt, self.foods)

            eaten = agent.try_eat(self.foods)
            if eaten is not None:
                self.foods.remove(eaten)
                self.foods.append(Food())  # respawn at random position
