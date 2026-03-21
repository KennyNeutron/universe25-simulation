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
)


class Agent:
    """A single autonomous agent that wanders and seeks food when hungry."""

    def __init__(self):
        # Random starting position (keep away from edges by one radius)
        self.x = random.uniform(AGENT_RADIUS, WINDOW_WIDTH - AGENT_RADIUS)
        self.y = random.uniform(AGENT_RADIUS, WINDOW_HEIGHT - AGENT_RADIUS)

        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3 * MAX_SPEED, MAX_SPEED)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Hunger state
        self.hunger = random.uniform(0, HUNGER_THRESHOLD * 0.5)

    def update(self, dt: float, foods: list) -> None:
        """Advance the agent by one time-step.

        Args:
            dt: Delta time in seconds since the last frame.
            foods: List of available Food objects in the simulation.
        """
        # Increase hunger over time
        self.hunger = min(self.hunger + HUNGER_RATE * dt, MAX_HUNGER)

        # Decide behavior based on hunger level
        if self.hunger >= HUNGER_THRESHOLD and foods:
            target = self._find_nearest(foods)
            if target is not None:
                self._seek(target, dt)
            else:
                self._wander(dt)
        else:
            self._wander(dt)

        self._clamp_speed()
        self._move(dt)
        self._bounce()

    def try_eat(self, foods: list):
        """Check if the agent is close enough to eat any food.

        Args:
            foods: List of available Food objects.

        Returns:
            The Food object that was eaten, or None.
        """
        eat_dist_sq = EAT_DISTANCE * EAT_DISTANCE
        for food in foods:
            dx = food.x - self.x
            dy = food.y - self.y
            if dx * dx + dy * dy <= eat_dist_sq:
                self.hunger = max(self.hunger - HUNGER_RESTORE, 0.0)
                return food
        return None

    # ── Private helpers ───────────────────────────────────────────────────

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

    def _seek(self, food, dt: float) -> None:
        """Steer velocity toward a target food item."""
        dx = food.x - self.x
        dy = food.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-6:
            return

        # Desired direction scaled by boosted max speed
        target_speed = MAX_SPEED * SEEK_SPEED_MULTIPLIER
        desired_vx = (dx / dist) * target_speed
        desired_vy = (dy / dist) * target_speed

        # Smoothly steer toward desired velocity
        steer_strength = 5.0  # how quickly agent turns toward food
        self.vx += (desired_vx - self.vx) * steer_strength * dt
        self.vy += (desired_vy - self.vy) * steer_strength * dt

    def _wander(self, dt: float) -> None:
        """Apply a small random acceleration to create wandering behavior."""
        angle = random.uniform(0, 2 * math.pi)
        self.vx += math.cos(angle) * WANDER_STRENGTH * dt
        self.vy += math.sin(angle) * WANDER_STRENGTH * dt

    def _clamp_speed(self) -> None:
        """Ensure the agent does not exceed its maximum speed."""
        max_spd = MAX_SPEED
        if self.hunger >= HUNGER_THRESHOLD:
            max_spd *= SEEK_SPEED_MULTIPLIER

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
