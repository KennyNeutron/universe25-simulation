import random


class Zone:
    """A rectangular region in the simulation world."""

    def __init__(self, zone_type: str, x: int, y: int, width: int, height: int):
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, px: float, py: float) -> bool:
        """Check if a point is inside this zone."""
        return (self.x <= px <= self.x + self.width
                and self.y <= py <= self.y + self.height)

    def random_point(self) -> tuple[float, float]:
        """Return a random (x, y) within this zone's bounds."""
        rx = random.uniform(self.x, self.x + self.width)
        ry = random.uniform(self.y, self.y + self.height)
        return rx, ry


class World:
    """Manages the structured environment (zones)."""

    def __init__(self, zone_defs: list[dict]):
        self.zones: list[Zone] = [
            Zone(z["type"], z["x"], z["y"], z["width"], z["height"])
            for z in zone_defs
        ]

    @property
    def feeding_zones(self) -> list[Zone]:
        """Return only the feeding-type zones."""
        return [z for z in self.zones if z.zone_type == "feeding"]

    @property
    def nesting_zones(self) -> list[Zone]:
        """Return only the nesting-type zones."""
        return [z for z in self.zones if z.zone_type == "nesting"]

    def random_food_position(self) -> tuple[float, float]:
        """Return a random position inside a random feeding zone."""
        feeding = self.feeding_zones
        zone = random.choice(feeding)
        return zone.random_point()
