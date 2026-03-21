import random
import math

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MAX_SPEED,
    WANDER_STRENGTH,
    AGENT_RADIUS,
)


class Agent:
    """A single autonomous agent that wanders within the simulation bounds."""

    def __init__(self):
        # Random starting position (keep away from edges by one radius)
        self.x = random.uniform(AGENT_RADIUS, WINDOW_WIDTH - AGENT_RADIUS)
        self.y = random.uniform(AGENT_RADIUS, WINDOW_HEIGHT - AGENT_RADIUS)

        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3 * MAX_SPEED, MAX_SPEED)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self, dt: float) -> None:
        """Advance the agent by one time-step.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        self._wander(dt)
        self._clamp_speed()
        self._move(dt)
        self._bounce()

    # ── Private helpers ───────────────────────────────────────────────────

    def _wander(self, dt: float) -> None:
        """Apply a small random acceleration to create wandering behavior."""
        angle = random.uniform(0, 2 * math.pi)
        self.vx += math.cos(angle) * WANDER_STRENGTH * dt
        self.vy += math.sin(angle) * WANDER_STRENGTH * dt

    def _clamp_speed(self) -> None:
        """Ensure the agent does not exceed its maximum speed."""
        speed_sq = self.vx * self.vx + self.vy * self.vy
        if speed_sq > MAX_SPEED * MAX_SPEED:
            speed = math.sqrt(speed_sq)
            scale = MAX_SPEED / speed
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
