import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    BACKGROUND_COLOR,
    AGENT_COLOR,
    AGENT_RADIUS,
)


class Renderer:
    """Handles all Pygame drawing for the simulation."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

    def render(self, agents) -> None:
        """Draw the current frame.

        Args:
            agents: Iterable of Agent objects to draw.
        """
        self.screen.fill(BACKGROUND_COLOR)

        for agent in agents:
            pygame.draw.circle(
                self.screen,
                AGENT_COLOR,
                (int(agent.x), int(agent.y)),
                AGENT_RADIUS,
            )

        pygame.display.flip()

    def close(self) -> None:
        """Shut down the Pygame display."""
        pygame.quit()
