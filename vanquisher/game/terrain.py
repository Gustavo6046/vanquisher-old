"""
This module is concerned with teh representation and generation
of specifically terrain. Every world.Chunk has a terrain property
of type TerrainChunk.
"""

import typing
import math
import random
import attr


def interpolate(low: float, high: float, alpha: float) -> float:
    """
    Linear interpolatino between two values.
    """

    return (high - low) * alpha + low


class TerrainChunk:
    """
    A square chunk of terrain. This is the terrain part of the game's
    concept of chunk. Chunk.terrain is a TerrainChunk.
    """

    def __init__(self, width=32, allow_height_interpolation=True):
        self.heightmap = [0.0 for _ in range(width * width)]
        self.width = width
        self.allow_height_interpolation = allow_height_interpolation

    def _get(self, x_pos: int, y_pos: int) -> float:
        return self.heightmap[y_pos * self.width + x_pos]

    def __getitem__(self, coords: typing.Tuple[float, float]) -> float:
        """
        Gets the height at any point of this TerrainChunk, including
        using bilinear interpolation if needed and allowed.
        """

        (x_pos, y_pos) = coords

        x_mid = x_pos % 1.0
        y_mid = y_pos % 1.0

        # Check if interpolation is not not allowed.
        if not self.allow_height_interpolation:
            # Interpolation is either disallowed or unnecessary.
            return self._get(int(x_pos), int(y_pos))

        # Find what interpolation may be required.
        interp = 0

        # - Check if interpolation is required in the X axis.
        if x_mid != 0.0:
            x_lo = math.floor(x_pos)
            x_hi = math.ceil(x_pos)

            interp |= 0b01

        # - Check if interpolation is required in the Y axis.
        if y_mid != 0.0:
            y_lo = math.floor(y_pos)
            y_hi = math.ceil(y_pos)

            interp |= 0b10

        # If interpolation is required in both axes,
        # do bilinear.

        if interp == 0b11:
            interm_1 = interpolate(self._get(x_lo, y_lo), self._get(x_lo, y_hi), x_mid)
            interm_2 = interpolate(self._get(x_hi, y_lo), self._get(x_hi, y_hi), x_mid)

            return interpolate(interm_1, interm_2, y_mid)

        # If interpolation is required in one axis,
        # do linear instead.

        if interp == 0b01:
            # ...on the X axis
            y_pos = int(y_pos)
            return interpolate(self._get(x_lo, y_pos), self._get(x_hi, y_pos), x_mid)

        if interp == 0b10:
            # ...on the Y axis
            x_pos = int(x_pos)
            return interpolate(self._get(x_pos, y_lo), self._get(x_pos, y_hi), y_mid)

        # Interpolatoin is not required.
        # Just fetch the value directly.
        return self._get(int(x_pos), int(y_pos))

    def __setitem__(self, pos: typing.Tuple[int, int], value: float):
        """
        Sets a value of this TerrainChunk heightmap.
        """

        (x_pos, y_pos) = pos
        self.heightmap[y_pos * self.width + x_pos] = value

    def generate(self, generator: "TerrainGenerator", offset: typing.Tuple[int, int] = (0, 0)):
        """
        Generates the heightmap of this terrain chunk from
        a TerrainGenerator instance.
        """

        x_offset, y_offset = offset

        for i_pos in range(self.width * self.width):
            x_pos = i_pos % self.width + x_offset
            y_pos = math.floor(i_pos / self.width) + y_offset

            self[x_pos, y_pos] = generator.height_at(x_pos, y_pos)


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
        max_distance = max_radius_sq ** (1/2)
        distance = distance_sq ** (1/2)

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


class TerrainGenerator:
    """
    Base TerrainGenerator class.

    This implementation is basic and can be overriden
    in subclasses.

    When subclassing, override '__init__' to change the
    parameters, and 'height_at' to change the algorithm itself.

    This example implementation puts much of its code in
    height_at.
    """

    def __init__(self, height: float, roughness: float, *peaks: Peak):
        """
        Initializes the TerrainGenerator's parameters. They are
        used when generating terrain later on.
        """

        self.height:    float = height
        self.roughness: float = roughness
        self.peaks:     typing.List[Peak] = list(peaks)

    def height_at(self, x_pos: int, y_pos: int) -> float:
        """
        For an X and Y coordinate, this generator uses its
        parameters to return a height value.
        """

        height = self.height + random.uniform(-self.roughness, self.roughness)

        for peak in self.peaks:
            height += peak.height_offset_at(self.height, x_pos, y_pos)

        return height
