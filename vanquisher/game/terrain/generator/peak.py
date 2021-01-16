"""
A lame peak-based terrain generator.
"""

import typing

import attr

from ....util import interpolate
from . import TerrainGenerator


@attr.s
class Peak:
    """
    A 'peak'. Used by the basic default implementation of
    TerrainGenerator, but can be used freely by subclasses,
    the latter including reassigning new meaning to values
    like strength and height.
    """

    x: float = attr.ib()
    y: float = attr.ib()
    strength: float = attr.ib(default=1.5)
    height: float = attr.ib(default=40)
    max_radius: float = attr.ib(default=32)
    lip: float = attr.ib(default=5)
    tip: float = attr.ib(default=9)

    def distance_squared(self, other_x: int, other_y: int) -> float:
        """
        Distance squared from this peak at any point.

        Distance 'squared', as in the square root is skipped.
        This does otherwise conform to the Pythagorean theorem.
        """

        off_x = self.x - other_x
        off_y = self.y - other_y

        return off_x ** 2 + off_y ** 2

    def height_offset_at(self, base_height: float, other_x: int, other_y: int) -> float:
        """
        Height offset of this peak at a particular point.
        'base_height' changes how the offset is calculated; the peak is meant
        to "rise" from that.
        """

        # max radius, squared, duh.
        max_radius_sq = self.max_radius ** 2

        # squared distance
        distance_sq = self.distance_squared(other_x, other_y)

        # but if too far, no do.
        if distance_sq >= max_radius_sq:
            return 0

        # falloff (reciprocal of the concrete strength)
        falloff = 1.0 + max(0, distance_sq ** (1 / (1 + self.strength)))

        val = (self.height - base_height) / falloff

        # some values
        max_distance = max_radius_sq ** (1 / 2)
        distance = distance_sq ** (1 / 2)

        edge_distance = max_distance - distance

        # tip (smoothing near the peak)
        if distance < self.tip:
            tip_crease = ((self.tip - distance) * 2 / self.tip) ** (1 + self.strength)
            val -= tip_crease

        # check for lipping
        if edge_distance < self.lip:
            # lip (smoothing near the border)
            lip_alpha = (self.lip - edge_distance) / self.lip

            val = interpolate(val, 0.0, lip_alpha)

        return val


class PeakTerrainGenerator(TerrainGenerator):
    """
    A TerrainGenerator implementation that uses 'peaks' in order
    to shape the terrain. Note that the peaks are not automatically
    generated and must be provided manually.

    This implementation is not recommended once a better one
    is available.
    """

    def setup(self, height: float, roughness: float, *peaks: Peak):
        """
        Initializes the TerrainGenerator's parameters. They are
        used when generating terrain later on.
        """

        self.height: float = height
        self.roughness: float = roughness
        self.peaks: typing.List[Peak] = list(peaks)

    def height_at(self, x_pos: int, y_pos: int) -> float:
        """
        For an X and Y coordinate, this generator uses its
        parameters to return a height value. In this case,
        it sums the heights of all peaks, plus a tiny
        random coarseness.
        """

        height = self.height + self.rng.uniform(-self.roughness, self.roughness)

        for peak in self.peaks:
            height += peak.height_offset_at(self.height, x_pos, y_pos)

        return height
