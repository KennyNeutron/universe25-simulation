import random

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FOOD_RADIUS


class Food:
    """A static food item that agents can consume."""

    def __init__(self):
        self.x = random.uniform(FOOD_RADIUS, WINDOW_WIDTH - FOOD_RADIUS)
        self.y = random.uniform(FOOD_RADIUS, WINDOW_HEIGHT - FOOD_RADIUS)
