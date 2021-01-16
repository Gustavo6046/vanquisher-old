"""
Terrain generation, is used whenever a chunk is
first loaded and does not have terrain in it yet.
"""


import abc
import random
import typing


class TerrainGenerator(abc.ABC):
    """
    Base TerrainGenerator class.

    The only method you need to override is `height_at`.
    You may want to define a `setup` function with any
    arguments in order to initialize parameters.

    This example implementation puts much of its code in
    height_at.
    """

    def __init__(self, seed: random.Random, *args, **kwargs):
        """
        Initializes this TerrainGenerator with a random
        number generator seed, and .
        """
        self.rng: random.random = random.Random(seed)
        self.setup(*args, **kwargs)

    @abc.abstractmethod
    def height_at(self, x_pos: int, y_pos: int) -> float:
        """
        For an X and Y coordinate, this generator uses its
        parameters to return a height value.
        """
        ...

    def setup(self, *args, **Kwargs):
        """
        Configures this TerrainGenerator based on the
        parameters that were passed to it.
        """
