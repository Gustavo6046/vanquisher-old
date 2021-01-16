"""
This module is concerned with teh representation and generation
of specifically terrain. Every world.Chunk has a terrain property
of type TerrainChunk.
"""

import math
import random
import typing

import attr

from ...util import interpolate


class TerrainChunk:
    """
    A square chunk of terrain. This is the terrain part of the game's
    concept of chunk. Chunk.terrain is a TerrainChunk.
    """

    def __init__(self, width=32, allow_height_interpolation=True):
        """
        Creates a new terrain, with the given square width and
        configuration, and with a heightmap that defaults to a flat
        plane with every point at height zero.

        You can then use a TerrainGenerator to make this terrain
        more interesting.
        """

        self.heightmap = [0.0 for _ in range(width * width)]
        self.width = width
        self.allow_height_interpolation = allow_height_interpolation

    def get(self, x_pos: int, y_pos: int) -> float:
        """
        Gets the height at the specified integer position of the
        heightmap. Use an indexing syntax instead unless you know
        what you are doing.
        """

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
            return self.get(int(x_pos), int(y_pos))

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
            interm_1 = interpolate(self.get(x_lo, y_lo), self.get(x_lo, y_hi), x_mid)
            interm_2 = interpolate(self.get(x_hi, y_lo), self.get(x_hi, y_hi), x_mid)

            return interpolate(interm_1, interm_2, y_mid)

        # If interpolation is required in one axis,
        # do linear instead.

        if interp == 0b01:
            # ...on the X axis
            y_pos = int(y_pos)
            return interpolate(self.get(x_lo, y_pos), self.get(x_hi, y_pos), x_mid)

        if interp == 0b10:
            # ...on the Y axis
            x_pos = int(x_pos)
            return interpolate(self.get(x_pos, y_lo), self.get(x_pos, y_hi), y_mid)

        # Interpolatoin is not required.
        # Just fetch the value directly.
        return self.get(int(x_pos), int(y_pos))

    def __setitem__(self, pos: typing.Tuple[int, int], value: float):
        """
        Sets a value of this TerrainChunk heightmap.
        """

        (x_pos, y_pos) = pos
        self.heightmap[y_pos * self.width + x_pos] = value

    def generate(
        self, generator: "TerrainGenerator", offset: typing.Tuple[int, int] = (0, 0)
    ):
        """
        Generates the heightmap of this terrain chunk from
        a TerrainGenerator instance.
        """

        x_offset, y_offset = offset

        for i_pos in range(self.width * self.width):
            x_pos = i_pos % self.width + x_offset
            y_pos = math.floor(i_pos / self.width) + y_offset

            self[x_pos, y_pos] = generator.height_at(x_pos, y_pos)
