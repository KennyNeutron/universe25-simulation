import random
import math

from agents.agent import Agent
from environment.food import Food
from environment.world import World
from config import (
    AGENT_COUNT,
    FOOD_COUNT,
    DENSITY_RADIUS,
    ZONES,
    WALLS,
    MATING_RADIUS,
    MAX_POPULATION,
    REPRODUCTION_DENSITY_PENALTY,
    BASE_REPRODUCTION_CHANCE,
    DEATH_FLASH_DURATION,
    INTERACTION_RADIUS,
    INTERACTION_COOLDOWN,
    INTERACTION_STRESS_POSITIVE,
    INTERACTION_STRESS_NEGATIVE,
    INTERACTION_FLASH_DURATION,
    MAX_STRESS,
    STRESS_THRESHOLD_MEDIUM,
    STRESS_THRESHOLD_HIGH,
    POSITIVE_CHANCE_LOW,
    NEGATIVE_CHANCE_LOW,
    POSITIVE_CHANCE_MED,
    NEGATIVE_CHANCE_MED,
    POSITIVE_CHANCE_HIGH,
    NEGATIVE_CHANCE_HIGH,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    EARLY_PHASE_DURATION,
    EARLY_STRESS_MULTIPLIER,
    EARLY_REPRODUCTION_STRESS_MAX,
    REPRODUCTION_STRESS_MAX,
    EARLY_REPRODUCTION_COOLDOWN,
    REPRODUCTION_COOLDOWN,
    LOG_INTERVAL,
)


class DeathMarker:
    """A brief visual marker at the location where an agent died."""
    __slots__ = ("x", "y", "timer")

    def __init__(self, x: float, y: float, duration: float):
        self.x = x
        self.y = y
        self.timer = duration


class InteractionFlash:
    """A brief visual marker at an interaction location."""
    __slots__ = ("x", "y", "color", "timer")

    def __init__(self, x: float, y: float, color: tuple, duration: float):
        self.x = x
        self.y = y
        self.color = color  # (R, G, B)
        self.timer = duration


class Simulation:
    """Manages agents, food, zones, reproduction, death, interactions, and the loop."""

    def __init__(self):
        self.world = World(ZONES, WALLS)
        
        # 8 original founders (Adam and Eves)
        self.agents: list[Agent] = []
        # 4 tightly clustered in Left Feeding Zone
        for _ in range(2):
            a1 = Agent(x=350 + random.uniform(-5, 5), y=320 + random.uniform(-5, 5))
            a1.gender = "male"
            self.agents.append(a1)
            a2 = Agent(x=350 + random.uniform(-5, 5), y=320 + random.uniform(-5, 5))
            a2.gender = "female"
            self.agents.append(a2)
        # 4 tightly clustered in Right Feeding Zone
        for _ in range(2):
            a3 = Agent(x=930 + random.uniform(-5, 5), y=320 + random.uniform(-5, 5))
            a3.gender = "male"
            self.agents.append(a3)
            a4 = Agent(x=930 + random.uniform(-5, 5), y=320 + random.uniform(-5, 5))
            a4.gender = "female"
            self.agents.append(a4)

        self.foods: list[Food] = [self._spawn_food() for _ in range(FOOD_COUNT)]
        self.death_markers: list[DeathMarker] = []
        self.interaction_flashes: list[InteractionFlash] = []

        # Lifecycle logging
        self.sim_time = 0.0
        self.log_timer = 0.0
        self.births_this_interval = 0
        self.deaths_this_interval = 0

    def update(self, dt: float) -> None:
        """Full simulation step: density, interactions, reproduction, agents, death."""
        self.sim_time += dt
        self.log_timer += dt
        
        phase_progress = min(1.0, self.sim_time / EARLY_PHASE_DURATION)
        
        # Lerp phase multipliers
        stress_mult = EARLY_STRESS_MULTIPLIER + (1.0 - EARLY_STRESS_MULTIPLIER) * phase_progress
        current_repro_stress_max = EARLY_REPRODUCTION_STRESS_MAX + (REPRODUCTION_STRESS_MAX - EARLY_REPRODUCTION_STRESS_MAX) * phase_progress
        current_repro_cooldown = EARLY_REPRODUCTION_COOLDOWN + (REPRODUCTION_COOLDOWN - EARLY_REPRODUCTION_COOLDOWN) * phase_progress

        if self.log_timer >= LOG_INTERVAL:
            print(f"[Time: {self.sim_time:5.1f}s] Pop: {len(self.agents):<4} | "
                  f"Births: {self.births_this_interval:<3} | Deaths: {self.deaths_this_interval:<3} | "
                  f"Phase: {phase_progress:.0%}")
            self.log_timer -= LOG_INTERVAL
            self.births_this_interval = 0
            self.deaths_this_interval = 0

        # ── Compute density, mating candidates, interaction candidates ────
        mating_pairs, interaction_pairs = self._compute_density_mates_interactions(current_repro_stress_max)

        # ── Process social interactions ───────────────────────────────────
        self._process_interactions(interaction_pairs, stress_mult)

        # ── Reproduction ──────────────────────────────────────────────────
        self._process_reproduction(dt, mating_pairs, current_repro_cooldown)

        # ── Update agents and handle eating ───────────────────────────────
        for agent in self.agents:
            agent.update(dt, self.foods, stress_mult)
            self._resolve_wall_collisions(agent)

            eaten = agent.try_eat(self.foods)
            if eaten is not None:
                self.foods.remove(eaten)
                self.foods.append(self._spawn_food())

        # ── Process deaths ────────────────────────────────────────────────
        self._process_deaths()

        # ── Decay visual markers ──────────────────────────────────────────
        for marker in self.death_markers:
            marker.timer -= dt
        self.death_markers = [m for m in self.death_markers if m.timer > 0]

        for flash in self.interaction_flashes:
            flash.timer -= dt
        self.interaction_flashes = [f for f in self.interaction_flashes if f.timer > 0]

    def _spawn_food(self) -> Food:
        """Create a new food item at a random position in a feeding zone."""
        x, y = self.world.random_food_position()
        return Food(x, y)

    def _resolve_wall_collisions(self, agent: Agent) -> None:
        """Prevent agents from passing through walls (AABB vs Circle)."""
        from config import AGENT_RADIUS
        import math
        radius = AGENT_RADIUS
        
        for wall in self.world.walls:
            # Find closest point on wall rect to agent center
            test_x = max(wall.x, min(agent.x, wall.x + wall.width))
            test_y = max(wall.y, min(agent.y, wall.y + wall.height))
            
            dist_x = agent.x - test_x
            dist_y = agent.y - test_y
            dist_sq = dist_x * dist_x + dist_y * dist_y
            
            if dist_sq < radius * radius:
                dist = math.sqrt(dist_sq)
                if dist == 0:
                    agent.y -= radius
                    agent.vy *= -1
                    continue
                    
                overlap = radius - dist
                nx = dist_x / dist
                ny = dist_y / dist
                
                # Push out
                agent.x += nx * overlap
                agent.y += ny * overlap
                
                # Reflect velocity (slide/bounce with low elasticity)
                dot = agent.vx * nx + agent.vy * ny
                if dot < 0:
                    agent.vx -= 1.2 * dot * nx
                    agent.vy -= 1.2 * dot * ny

    def _process_deaths(self) -> None:
        """Remove dead agents and create death markers."""
        surviving = []
        for agent in self.agents:
            if agent.is_dead:
                print(f"[DEATH] age={agent.age:.1f}, hunger={agent.hunger:.1f}, pos={agent.x:.1f},{agent.y:.1f}, stress={agent.stress:.1f}")
                agent.alive = False
                self.death_markers.append(
                    DeathMarker(agent.x, agent.y, DEATH_FLASH_DURATION)
                )
                self.deaths_this_interval += 1
            else:
                surviving.append(agent)
        self.agents = surviving

    def _compute_density_mates_interactions(self, current_repro_stress_max: float):
        """One O(n²) pass: density counts, mating pairs, interaction pairs,
        and nearby-agent lists for avoidance."""
        agents = self.agents
        n = len(agents)
        density_sq = DENSITY_RADIUS * DENSITY_RADIUS
        mating_sq = MATING_RADIUS * MATING_RADIUS
        interact_sq = INTERACTION_RADIUS * INTERACTION_RADIUS

        mating_pairs: list[tuple[Agent, Agent]] = []
        interaction_pairs: list[tuple[Agent, Agent]] = []

        for a in agents:
            a.neighbor_count = 0
            a.nearby_agents = []

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
                    ai.nearby_agents.append(aj)
                    aj.nearby_agents.append(ai)

                if (dist_sq <= mating_sq
                        and ai.gender != aj.gender
                        and ai.can_reproduce(current_repro_stress_max)
                        and aj.can_reproduce(current_repro_stress_max)):
                    mating_pairs.append((ai, aj))

                if (dist_sq <= interact_sq
                        and ai.interaction_cooldown <= 0
                        and aj.interaction_cooldown <= 0):
                    interaction_pairs.append((ai, aj))

        return mating_pairs, interaction_pairs

    def _process_interactions(self, pairs: list[tuple[Agent, Agent]], stress_mult: float) -> None:
        """Resolve social interactions and apply stress/repulsion outcomes."""
        random.shuffle(pairs)
        processed = set()  # avoid double-interaction per frame

        for a, b in pairs:
            if id(a) in processed or id(b) in processed:
                continue

            # Determine outcome based on average stress
            avg_stress = (a.stress + b.stress) / 2
            if avg_stress >= STRESS_THRESHOLD_HIGH:
                pos_chance = POSITIVE_CHANCE_HIGH
                neg_chance = NEGATIVE_CHANCE_HIGH
            elif avg_stress >= STRESS_THRESHOLD_MEDIUM:
                pos_chance = POSITIVE_CHANCE_MED
                neg_chance = NEGATIVE_CHANCE_MED
            else:
                pos_chance = POSITIVE_CHANCE_LOW
                neg_chance = NEGATIVE_CHANCE_LOW

            roll = random.random()
            mid_x = (a.x + b.x) / 2
            mid_y = (a.y + b.y) / 2

            if roll < pos_chance:
                # Positive interaction — slight stress relief
                a.stress = max(0.0, a.stress + INTERACTION_STRESS_POSITIVE)
                b.stress = max(0.0, b.stress + INTERACTION_STRESS_POSITIVE)
                self.interaction_flashes.append(
                    InteractionFlash(mid_x, mid_y, (80, 255, 80), INTERACTION_FLASH_DURATION)
                )
            elif roll < pos_chance + neg_chance:
                # Negative interaction — stress gain + repulsion
                negative_impact = INTERACTION_STRESS_NEGATIVE * stress_mult
                a.stress = min(MAX_STRESS, a.stress + negative_impact)
                b.stress = min(MAX_STRESS, b.stress + negative_impact)
                a.apply_repulsion(b)
                b.apply_repulsion(a)
                self.interaction_flashes.append(
                    InteractionFlash(mid_x, mid_y, (255, 60, 60), INTERACTION_FLASH_DURATION)
                )
            # else: neutral — no effect

            a.interaction_cooldown = INTERACTION_COOLDOWN
            b.interaction_cooldown = INTERACTION_COOLDOWN
            processed.add(id(a))
            processed.add(id(b))

    def _process_reproduction(self, dt: float,
                              mating_pairs: list[tuple[Agent, Agent]],
                              current_repro_cooldown: float) -> None:
        """Attempt reproduction for eligible pairs (at most 1 birth per frame)."""
        if len(self.agents) >= MAX_POPULATION:
            return

        random.shuffle(mating_pairs)

        for parent_a, parent_b in mating_pairs:
            if not (parent_a.can_reproduce and parent_b.can_reproduce):
                continue

            avg_neighbors = (parent_a.neighbor_count + parent_b.neighbor_count) / 2
            from config import REPRODUCTION_DENSITY_PENALTY
            chance = BASE_REPRODUCTION_CHANCE * dt * max(
                0.0, 1.0 - avg_neighbors * REPRODUCTION_DENSITY_PENALTY
            )

            if random.random() < chance:
                child = Agent.create_child(parent_a, parent_b, current_repro_cooldown)
                self.agents.append(child)
                self.births_this_interval += 1
                break
