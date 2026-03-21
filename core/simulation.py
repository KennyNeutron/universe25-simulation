import random

from agents.agent import Agent
from environment.food import Food
from environment.world import World
from config import (
    AGENT_COUNT,
    FOOD_COUNT,
    DENSITY_RADIUS,
    ZONES,
    MATING_RADIUS,
    MAX_POPULATION,
    REPRODUCTION_DENSITY_PENALTY,
    BASE_REPRODUCTION_CHANCE,
)


class Simulation:
    """Manages agents, food, world zones, reproduction, and drives the loop."""

    def __init__(self):
        self.world = World(ZONES)
        self.agents: list[Agent] = [Agent() for _ in range(AGENT_COUNT)]
        self.foods: list[Food] = [self._spawn_food() for _ in range(FOOD_COUNT)]

    def update(self, dt: float) -> None:
        """Update density, reproduction, agents, and handle eating / food respawn.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        # ── Compute neighbor density + collect mating candidates ──────────
        mating_pairs = self._compute_density_and_mates()

        # ── Reproduction ──────────────────────────────────────────────────
        self._process_reproduction(dt, mating_pairs)

        # ── Update agents and handle eating ───────────────────────────────
        for agent in self.agents:
            agent.update(dt, self.foods)

            eaten = agent.try_eat(self.foods)
            if eaten is not None:
                self.foods.remove(eaten)
                self.foods.append(self._spawn_food())

    def _spawn_food(self) -> Food:
        """Create a new food item at a random position in a feeding zone."""
        x, y = self.world.random_food_position()
        return Food(x, y)

    def _compute_density_and_mates(self) -> list[tuple[Agent, Agent]]:
        """Count neighbors + collect eligible mating pairs in one O(n²) pass."""
        agents = self.agents
        n = len(agents)
        density_sq = DENSITY_RADIUS * DENSITY_RADIUS
        mating_sq = MATING_RADIUS * MATING_RADIUS
        mating_pairs: list[tuple[Agent, Agent]] = []

        # Reset counts
        for a in agents:
            a.neighbor_count = 0

        for i in range(n):
            ai = agents[i]
            for j in range(i + 1, n):
                aj = agents[j]
                dx = ai.x - aj.x
                dy = ai.y - aj.y
                dist_sq = dx * dx + dy * dy

                if dist_sq <= density_sq:
                    ai.neighbor_count += 1
                    aj.neighbor_count += 1

                # Mating candidate check (tighter radius)
                if (dist_sq <= mating_sq
                        and ai.gender != aj.gender
                        and ai.can_reproduce
                        and aj.can_reproduce):
                    mating_pairs.append((ai, aj))

        return mating_pairs

    def _process_reproduction(self, dt: float,
                              mating_pairs: list[tuple[Agent, Agent]]) -> None:
        """Attempt reproduction for eligible pairs (at most 1 birth per frame)."""
        if len(self.agents) >= MAX_POPULATION:
            return

        random.shuffle(mating_pairs)

        for parent_a, parent_b in mating_pairs:
            # Re-check eligibility (a parent may have been used this frame)
            if not (parent_a.can_reproduce and parent_b.can_reproduce):
                continue

            # Density penalty — average neighbor count of the pair
            avg_neighbors = (parent_a.neighbor_count + parent_b.neighbor_count) / 2
            chance = BASE_REPRODUCTION_CHANCE * dt * max(
                0.0, 1.0 - avg_neighbors * REPRODUCTION_DENSITY_PENALTY
            )

            if random.random() < chance:
                child = Agent.create_child(parent_a, parent_b)
                self.agents.append(child)
                break  # at most 1 birth per frame
