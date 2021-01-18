"""Vanquisher base terrain code.

This module is concerned with the representation and generation
of specifically terrain. Every world.Chunk has a terrain property
of type TerrainChunk.
"""

import math
import typing

from ...util import interpolate

if typing.TYPE_CHECKING:
    from . import generator


class TerrainChunk:
    """A square chunk of terrain.

    This is the terrain part of the game's concept of chunk.
    You can tell because Chunk.terrain is always a TerrainChunk.
    """

    def __init__(self, width=32):
        """TerrainChunk initializer.

        Creates a new terrain, with the given square width and
        configuration, and with a heightmap that defaults to a flat
        plane with every point at height zero.

        You can then use a TerrainGenerator to make this terrain
        more interesting.

        In general, though, let World handle this job, unless you
        really want to use TerrainChunk directly and manually.
        """

        self.heightmap = [0.0 for _ in range(width * width)]
        self.width = width

    def get(self, x_pos: int, y_pos: int) -> float:
        """A terrain height getter, at aligned (integer) positions, without interpolation.

        Gets the height at the specified integer position of the
        heightmap. Use an indexing syntax instead unless you know
        what you are doing.
        """

        return self.heightmap[y_pos * self.width + x_pos]

    def __getitem__(self, coords: typing.Tuple[float, float]) -> float:
        """A terrain height getter.

        Gets the height at any point of this TerrainChunk, including
        using bilinear interpolation.
        """

        (x_pos, y_pos) = coords

        x_mid = x_pos % 1.0
        y_mid = y_pos % 1.0

        # Cannot interpolate between chunks ... yet.
        if x_pos < 0.0:
            x_pos = 0.0

        if x_pos > self.width - 1.0:
            x_pos = self.width - 1.0

        if y_pos < 0.0:
            y_pos = 0.0

        if y_pos > self.width - 1.0:
            y_pos = self.width - 1.0

        # Do bilinear interpolation.
        x_lo = math.floor(x_pos)
        x_hi = math.ceil(x_pos)
        y_lo = math.floor(y_pos)
        y_hi = math.ceil(y_pos)

        interm_1 = interpolate(self.get(x_lo, y_lo), self.get(x_lo, y_hi), x_mid)
        interm_2 = interpolate(self.get(x_hi, y_lo), self.get(x_hi, y_hi), x_mid)

        return interpolate(interm_1, interm_2, y_mid)

    def __setitem__(self, pos: typing.Tuple[int, int], value: float):
        """Sets a value of this TerrainChunk heightmap."""

        (x_pos, y_pos) = pos
        self.heightmap[y_pos * self.width + x_pos] = value

    def generate(
        self,
        generator: "generator.TerrainGenerator",
        offset: typing.Tuple[int, int] = (0, 0),
    ):
        """Generate the heightmap according to the passed TerrainGenerator.

        Generates the heightmap of this terrain chunk from
        a TerrainGenerator instance.
        """

        x_offset, y_offset = offset

        for i_pos in range(self.width * self.width):
            x_pos = i_pos % self.width
            y_pos = math.floor(i_pos / self.width)

            self[x_pos, y_pos] = generator.height_at(x_pos + x_offset, y_pos + y_offset)
