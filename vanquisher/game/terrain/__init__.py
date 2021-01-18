"""Vanquisher base terrain code.

This module is concerned with the representation and generation
of specifically terrain. Every world.Chunk has a terrain property
of type TerrainChunk.
"""

import ctypes
import math
import typing

from ...numba import maybe_numba_jit

if typing.TYPE_CHECKING:
    from . import generator

try:
    from ._interpolate.lib import bilinear

    USE_CFFI_INTERPOLATOR = True

except ImportError:
    USE_CFFI_INTERPOLATOR = False


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

        self.heightmap = (ctypes.c_float * (width * width))()
        self.width = width

    def get(self, x_pos: int, y_pos: int) -> float:
        """A terrain height getter, at aligned (integer) positions, uninterpolated.

        Gets the height at the specified integer position of the
        heightmap. Use an indexing syntax instead unless you know
        what you are doing.
        """
        return self.heightmap[y_pos * self.width + x_pos]

    @staticmethod
    @maybe_numba_jit(nopython=True)
    def _bilinear_interpolate(
        val_a: float,
        val_b: float,
        val_c: float,
        val_d: float,
        x_pos: float,
        y_pos: float,
        x_lo: float,
        x_hi: float,
        y_lo: float,
        y_hi: float,
    ) -> float:
        """Bilinear interpolation without fuss. Made for Numba."""
        weight_a = (x_hi - x_pos) * (y_hi - y_pos)
        weight_b = (x_hi - x_pos) * (y_pos - y_lo)
        weight_c = (x_pos - x_lo) * (y_hi - y_pos)
        weight_d = (x_pos - x_lo) * (y_pos - y_lo)

        return weight_a * val_a + weight_b * val_b + weight_c * val_c + weight_d * val_d

    def __getitem__(self, coords: typing.Tuple[float, float]) -> float:
        """A terrain height getter.

        Gets the height at any point of this TerrainChunk, including
        using bilinear interpolation.

        Uses the Cython interpolator whenever possible.
        """

        if USE_CFFI_INTERPOLATOR:
            return bilinear(self.width, *coords, ctypes.pointer(self.heightmap))

        (x_pos, y_pos) = coords

        if x_pos < 0.0:
            x_pos = 0.0

        if x_pos > self.width - 1.0:
            x_pos = self.width - 1.0001  # tiny epsilon for flooring purposes

        if y_pos < 0.0:
            y_pos = 0.0

        if y_pos > self.width - 1.0:
            y_pos = self.width - 1.0001  # tiny epsilon for flooring purposes

        x_lo = math.floor(x_pos)
        x_hi = x_lo + 1
        y_lo = math.floor(y_pos)
        y_hi = y_lo + 1

        val_a = self.get(x_lo, y_lo)
        val_b = self.get(x_lo, y_hi)
        val_c = self.get(x_hi, y_lo)
        val_d = self.get(x_hi, y_hi)

        return self._bilinear_interpolate(
            val_a, val_b, val_c, val_d, x_pos, y_pos, x_lo, x_hi, y_lo, y_hi
        )

    def __setitem__(self, pos: typing.Tuple[int, int], value: float):
        """Sets a value of this TerrainChunk heightmap."""

        (x_pos, y_pos) = pos

        self.heightmap[y_pos * self.width + x_pos] = value

    @maybe_numba_jit(nopython=False)
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
