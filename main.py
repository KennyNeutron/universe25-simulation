"""Universe 25 Simulation — Entry Point"""

import sys
import pygame

from config import FPS
from core.simulation import Simulation
from visualization.renderer import Renderer


def main() -> None:
    simulation = Simulation()
    renderer = Renderer()
    clock = pygame.time.Clock()

    running = True
    while running:
        # ── Event handling ────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ── Update ────────────────────────────────────────────────────────
        dt = clock.get_time() / 1000.0  # milliseconds → seconds
        simulation.update(dt)

        # ── Render ────────────────────────────────────────────────────────
        renderer.render(simulation.agents, simulation.foods, simulation.world)

        # ── Tick ──────────────────────────────────────────────────────────
        clock.tick(FPS)

    renderer.close()
    sys.exit()


if __name__ == "__main__":
    main()
