import math

import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    BACKGROUND_COLOR,
    MOUSE_SPRITE_SIZE,
    FOOD_SPRITE_SIZE,
)


def _create_mouse_sprite(size: tuple[int, int]) -> pygame.Surface:
    """Create a top-down mouse sprite programmatically (facing right)."""
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    cx, cy = w // 2, h // 2

    # Body — light gray ellipse
    body_rect = pygame.Rect(cx - w // 3, cy - h // 4, int(w * 0.6), h // 2)
    pygame.draw.ellipse(surf, (180, 175, 170), body_rect)

    # Head — smaller circle toward the right
    head_r = int(w * 0.2)
    head_cx = cx + w // 4
    pygame.draw.circle(surf, (190, 185, 180), (head_cx, cy), head_r)

    # Ears — two small pink circles
    ear_r = max(2, int(w * 0.1))
    pygame.draw.circle(surf, (240, 180, 180), (head_cx - 1, cy - head_r), ear_r)
    pygame.draw.circle(surf, (240, 180, 180), (head_cx + 2, cy - head_r), ear_r)

    # Eye — tiny black dot
    pygame.draw.circle(surf, (30, 30, 30), (head_cx + 1, cy - 1), max(1, w // 16))

    # Tail — thin line toward the left
    tail_start = (cx - w // 3, cy)
    tail_end = (1, cy + h // 4)
    pygame.draw.line(surf, (200, 170, 170), tail_start, tail_end, max(1, w // 16))

    return surf


def _create_food_sprite(size: tuple[int, int]) -> pygame.Surface:
    """Create a small cheese-wedge food sprite programmatically."""
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    cx, cy = w // 2, h // 2

    # Cheese wedge — yellow filled circle
    r = min(w, h) // 2 - 1
    pygame.draw.circle(surf, (240, 210, 60), (cx, cy), r)

    # Holes — two tiny dark-yellow dots
    hole_r = max(1, r // 4)
    pygame.draw.circle(surf, (200, 170, 30), (cx - hole_r, cy), hole_r)
    pygame.draw.circle(surf, (200, 170, 30), (cx + hole_r, cy - hole_r), max(1, hole_r - 1))

    return surf


class Renderer:
    """Handles all Pygame drawing for the simulation using sprite images."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        # Create sprites once (proper transparency guaranteed)
        self.mouse_sprite = _create_mouse_sprite(MOUSE_SPRITE_SIZE)
        self.food_sprite = _create_food_sprite(FOOD_SPRITE_SIZE)

        # Pre-compute half sizes for centering food
        self._food_half_w = FOOD_SPRITE_SIZE[0] // 2
        self._food_half_h = FOOD_SPRITE_SIZE[1] // 2

    def render(self, agents, foods) -> None:
        """Draw the current frame.

        Args:
            agents: Iterable of Agent objects to draw.
            foods: Iterable of Food objects to draw.
        """
        self.screen.fill(BACKGROUND_COLOR)

        # Draw food first (underneath agents)
        for food in foods:
            self.screen.blit(
                self.food_sprite,
                (int(food.x) - self._food_half_w,
                 int(food.y) - self._food_half_h),
            )

        # Draw agents on top, rotated to face movement direction
        for agent in agents:
            angle = math.degrees(math.atan2(-agent.vy, agent.vx))
            rotated = pygame.transform.rotate(self.mouse_sprite, angle)
            rect = rotated.get_rect(center=(int(agent.x), int(agent.y)))
            self.screen.blit(rotated, rect)

        pygame.display.flip()

    def close(self) -> None:
        """Shut down the Pygame display."""
        pygame.quit()
