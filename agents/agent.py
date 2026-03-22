import random
import math

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MAX_SPEED,
    WANDER_STRENGTH,
    AGENT_RADIUS,
    HUNGER_RATE,
    HUNGER_THRESHOLD,
    MAX_HUNGER,
    HUNGER_RESTORE,
    SEEK_SPEED_MULTIPLIER,
    EAT_DISTANCE,
    MAX_STRESS,
    STRESS_DECAY_RATE,
    STRESS_PER_NEIGHBOR,
    STRESS_THRESHOLD_MEDIUM,
    STRESS_THRESHOLD_HIGH,
    STRESS_JITTER_MEDIUM,
    STRESS_JITTER_HIGH,
    STRESS_SEEK_PENALTY_MEDIUM,
    STRESS_SEEK_PENALTY_HIGH,
    STRESS_WANDER_CHANCE_HIGH,
    REPRODUCTION_COOLDOWN,
    REPRODUCTION_STRESS_MAX,
    REPRODUCTION_HUNGER_MAX,
    CHILD_SPEED_VARIATION,
    BIRTH_FLASH_DURATION,
    AGENT_LIFESPAN,
    LIFESPAN_VARIATION,
    STARVATION_THRESHOLD,
    BEHAVIORAL_SINK_THRESHOLD,
    SINK_SEEK_CHANCE,
    SINK_SPEED_PENALTY,
    STRESS_RECOVERY_DELAY,
    INTERACTION_COOLDOWN,
    INTERACTION_REPULSION,
    AVOIDANCE_THRESHOLD,
    AVOIDANCE_STRENGTH,
)


class Agent:
    """A single autonomous agent with hunger, stress, reproduction, death,
    social interactions, and behavioral degradation."""

    def __init__(self, x: float = None, y: float = None, max_speed: float = None):
        # Position
        self.x = x if x is not None else random.uniform(100, WINDOW_WIDTH - 100)
        self.y = y if y is not None else random.uniform(100, WINDOW_HEIGHT - 100)

        # Per-agent max speed (for inheritance)
        self.max_speed = max_speed if max_speed is not None else MAX_SPEED

        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3 * self.max_speed, self.max_speed)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Hunger state
        self.hunger = random.uniform(0, HUNGER_THRESHOLD * 0.5)

        # Stress state
        self.stress = 0.0
        self.neighbor_count = 0  # set externally by Simulation
        self.stress_recovery_timer = 0.0

        # Identity & reproduction
        self.gender = random.choice(["male", "female"])
        self.age = 0.0
        self.lifespan = AGENT_LIFESPAN * random.uniform(
            1.0 - LIFESPAN_VARIATION, 1.0 + LIFESPAN_VARIATION
        )
        self.reproduction_cooldown = REPRODUCTION_COOLDOWN * 0.5
        self.birth_flash = 0.0

        # Death
        self.alive = True

        # Social
        self.interaction_cooldown = 0.0
        self.nearby_agents: list["Agent"] = []  # set externally for avoidance

    @property
    def stress_ratio(self) -> float:
        """Normalized stress level in [0, 1] for rendering."""
        return self.stress / MAX_STRESS

    @property
    def is_dead(self) -> bool:
        """Check if this agent should die this frame."""
        return self.hunger >= STARVATION_THRESHOLD or self.age >= self.lifespan

    @property
    def can_reproduce(self) -> bool:
        """Check if this agent is eligible to reproduce right now."""
        return (
            self.alive
            and self.reproduction_cooldown <= 0
            and self.stress < REPRODUCTION_STRESS_MAX
            and self.hunger < REPRODUCTION_HUNGER_MAX
        )

    @classmethod
    def create_child(cls, parent_a: "Agent", parent_b: "Agent") -> "Agent":
        """Spawn a child near the midpoint of two parents with inherited traits."""
        mx = (parent_a.x + parent_b.x) / 2 + random.uniform(-10, 10)
        my = (parent_a.y + parent_b.y) / 2 + random.uniform(-10, 10)
        mx = max(AGENT_RADIUS, min(mx, WINDOW_WIDTH - AGENT_RADIUS))
        my = max(AGENT_RADIUS, min(my, WINDOW_HEIGHT - AGENT_RADIUS))

        avg_speed = (parent_a.max_speed + parent_b.max_speed) / 2
        variation = avg_speed * CHILD_SPEED_VARIATION
        child_speed = avg_speed + random.uniform(-variation, variation)
        child_speed = max(child_speed, MAX_SPEED * 0.5)

        child = cls(x=mx, y=my, max_speed=child_speed)
        child.hunger = 0.0
        child.stress = 0.0
        child.age = 0.0
        child.reproduction_cooldown = REPRODUCTION_COOLDOWN
        child.birth_flash = BIRTH_FLASH_DURATION

        parent_a.reproduction_cooldown = REPRODUCTION_COOLDOWN
        parent_b.reproduction_cooldown = REPRODUCTION_COOLDOWN

        return child

    def apply_repulsion(self, other: "Agent") -> None:
        """Push this agent's velocity away from another agent."""
        dx = self.x - other.x
        dy = self.y - other.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-6:
            angle = random.uniform(0, 2 * math.pi)
            dx, dy = math.cos(angle), math.sin(angle)
            dist = 1.0
        self.vx += (dx / dist) * INTERACTION_REPULSION
        self.vy += (dy / dist) * INTERACTION_REPULSION

    def update(self, dt: float, foods: list) -> None:
        """Advance the agent by one time-step."""
        # ── Timers ────────────────────────────────────────────────────────
        self.age += dt
        self.reproduction_cooldown = max(0.0, self.reproduction_cooldown - dt)
        self.interaction_cooldown = max(0.0, self.interaction_cooldown - dt)
        self.birth_flash = max(0.0, self.birth_flash - dt)

        # ── Stress accumulation / recovery ────────────────────────────────
        self.stress += self.neighbor_count * STRESS_PER_NEIGHBOR * dt

        if self.neighbor_count == 0:
            self.stress_recovery_timer += dt
        else:
            self.stress_recovery_timer = 0.0

        if self.stress_recovery_timer >= STRESS_RECOVERY_DELAY:
            self.stress -= STRESS_DECAY_RATE * dt

        self.stress = max(0.0, min(self.stress, MAX_STRESS))

        # ── Hunger ────────────────────────────────────────────────────────
        self.hunger = min(self.hunger + HUNGER_RATE * dt, MAX_HUNGER)

        # ── Behavior (4-tier stress degradation + avoidance) ──────────────
        self._behave(dt, foods)

        self._clamp_speed()
        self._move(dt)
        self._bounce()

    def try_eat(self, foods: list):
        """Check if the agent is close enough to eat any food."""
        eat_dist_sq = EAT_DISTANCE * EAT_DISTANCE
        for food in foods:
            dx = food.x - self.x
            dy = food.y - self.y
            if dx * dx + dy * dy <= eat_dist_sq:
                self.hunger = max(self.hunger - HUNGER_RESTORE, 0.0)
                return food
        return None

    # ── Private helpers ───────────────────────────────────────────────────

    def _behave(self, dt: float, foods: list) -> None:
        """Decide movement behavior based on hunger and stress level (4 tiers)."""
        wants_food = self.hunger >= HUNGER_THRESHOLD and foods

        # Social avoidance: high-stress agents flee neighbors when not eating
        if (self.stress >= AVOIDANCE_THRESHOLD
                and self.nearby_agents
                and not wants_food):
            self._avoid_neighbors(dt)
            self._apply_jitter(dt, STRESS_JITTER_HIGH)
            return

        if self.stress >= BEHAVIORAL_SINK_THRESHOLD:
            # BEHAVIORAL SINK: agent nearly non-functional
            if wants_food and random.random() < SINK_SEEK_CHANCE:
                target = self._find_nearest(foods)
                if target is not None:
                    self._seek(target, dt, STRESS_SEEK_PENALTY_HIGH)
                else:
                    self._wander(dt)
            else:
                # Even when in sink, prefer avoidance if neighbors present
                if self.nearby_agents:
                    self._avoid_neighbors(dt)
                else:
                    self._wander(dt)
            self._apply_jitter(dt, STRESS_JITTER_HIGH)

        elif self.stress >= STRESS_THRESHOLD_HIGH:
            if wants_food and random.random() > STRESS_WANDER_CHANCE_HIGH:
                target = self._find_nearest(foods)
                if target is not None:
                    self._seek(target, dt, STRESS_SEEK_PENALTY_HIGH)
                else:
                    self._wander(dt)
            else:
                self._wander(dt)
            self._apply_jitter(dt, STRESS_JITTER_HIGH)

        elif self.stress >= STRESS_THRESHOLD_MEDIUM:
            if wants_food:
                target = self._find_nearest(foods)
                if target is not None:
                    self._seek(target, dt, STRESS_SEEK_PENALTY_MEDIUM)
                else:
                    self._wander(dt)
            else:
                self._wander(dt)
            self._apply_jitter(dt, STRESS_JITTER_MEDIUM)

        else:
            if wants_food:
                target = self._find_nearest(foods)
                if target is not None:
                    self._seek(target, dt, 1.0)
                else:
                    self._wander(dt)
            else:
                self._wander(dt)

    def _avoid_neighbors(self, dt: float) -> None:
        """Steer away from the center of nearby agents (social avoidance)."""
        if not self.nearby_agents:
            return
        avg_x = sum(a.x for a in self.nearby_agents) / len(self.nearby_agents)
        avg_y = sum(a.y for a in self.nearby_agents) / len(self.nearby_agents)
        dx = self.x - avg_x
        dy = self.y - avg_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-6:
            angle = random.uniform(0, 2 * math.pi)
            dx, dy = math.cos(angle), math.sin(angle)
            dist = 1.0
        flee_speed = self.max_speed
        desired_vx = (dx / dist) * flee_speed
        desired_vy = (dy / dist) * flee_speed
        self.vx += (desired_vx - self.vx) * AVOIDANCE_STRENGTH * dt
        self.vy += (desired_vy - self.vy) * AVOIDANCE_STRENGTH * dt

    def _find_nearest(self, foods: list):
        """Return the nearest food item via linear distance scan."""
        nearest = None
        nearest_dist_sq = float("inf")
        for food in foods:
            dx = food.x - self.x
            dy = food.y - self.y
            dist_sq = dx * dx + dy * dy
            if dist_sq < nearest_dist_sq:
                nearest_dist_sq = dist_sq
                nearest = food
        return nearest

    def _seek(self, food, dt: float, efficiency: float = 1.0) -> None:
        """Steer velocity toward a target food item."""
        dx = food.x - self.x
        dy = food.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-6:
            return

        target_speed = self.max_speed * SEEK_SPEED_MULTIPLIER
        desired_vx = (dx / dist) * target_speed
        desired_vy = (dy / dist) * target_speed

        steer_strength = 5.0 * efficiency
        self.vx += (desired_vx - self.vx) * steer_strength * dt
        self.vy += (desired_vy - self.vy) * steer_strength * dt

    def _wander(self, dt: float) -> None:
        """Apply a small random acceleration to create wandering behavior."""
        angle = random.uniform(0, 2 * math.pi)
        self.vx += math.cos(angle) * WANDER_STRENGTH * dt
        self.vy += math.sin(angle) * WANDER_STRENGTH * dt

    def _apply_jitter(self, dt: float, strength: float) -> None:
        """Add extra random noise proportional to stress-level strength."""
        angle = random.uniform(0, 2 * math.pi)
        jitter = WANDER_STRENGTH * strength
        self.vx += math.cos(angle) * jitter * dt
        self.vy += math.sin(angle) * jitter * dt

    def _clamp_speed(self) -> None:
        """Ensure the agent does not exceed its maximum speed."""
        max_spd = self.max_speed
        if self.hunger >= HUNGER_THRESHOLD:
            max_spd *= SEEK_SPEED_MULTIPLIER

        if self.stress >= BEHAVIORAL_SINK_THRESHOLD:
            max_spd *= SINK_SPEED_PENALTY

        speed_sq = self.vx * self.vx + self.vy * self.vy
        if speed_sq > max_spd * max_spd:
            speed = math.sqrt(speed_sq)
            scale = max_spd / speed
            self.vx *= scale
            self.vy *= scale

    def _move(self, dt: float) -> None:
        """Update position based on current velocity."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def _bounce(self) -> None:
        """Reflect velocity and clamp position at screen boundaries."""
        if self.x < AGENT_RADIUS:
            self.x = AGENT_RADIUS
            self.vx = abs(self.vx)
        elif self.x > WINDOW_WIDTH - AGENT_RADIUS:
            self.x = WINDOW_WIDTH - AGENT_RADIUS
            self.vx = -abs(self.vx)

        if self.y < AGENT_RADIUS:
            self.y = AGENT_RADIUS
            self.vy = abs(self.vy)
        elif self.y > WINDOW_HEIGHT - AGENT_RADIUS:
            self.y = WINDOW_HEIGHT - AGENT_RADIUS
            self.vy = -abs(self.vy)
