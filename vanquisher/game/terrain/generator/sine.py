"""A lame sine wave terrain generator."""

import math
import typing

from . import TerrainGenerator


class PeakTerrainGenerator(TerrainGenerator):
    """A TerrainGenerator implementation that creates wavy terrain using sine waves.

    Nothing is randomized, so seed is unused.

    This implementation is not recommended once a better one
    is available.
    """

    def __init__(
        self,
        seed: int,
        base_height: float = 20.0,
        period: float = 9.0,
        amplitude: float = 7.5,
        x_scale: float = 1.0,
        y_scale: float = 1.2
    ):
        """Initialize the PeakTerrainGenerator's parameters."""
        super().__init__(seed)

        self.frequency: float = math.pi * 2.0 / period
        self.amplitude: float = amplitude
        self.base_height: float = base_height

        self.x_scale: float = x_scale
        self.y_scale: float = y_scale

    def height_at(self, x_pos: int, y_pos: int) -> float:
        """Finds a height at a specific X and Y position in the terrain height grid.

        This generator averages two sine waves, one along the X axis, and
        one along the Y axis.
        """
        return self.base_height + self.amplitude * (
            math.sin(x_pos * self.frequency * self.x_scale) +
            math.sin(y_pos * self.frequency * self.y_scale)
        ) / 2
