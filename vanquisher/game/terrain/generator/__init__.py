"""
Terrain generation, is used whenever a chunk is
first loaded and does not have terrain in it yet.
"""


import abc
import random


class TerrainGenerator(abc.ABC):
    """
    Base TerrainGenerator class.

    The only method you need to override is `height_at`.
    You may want to define a `__init__` function in order
    to initialize parameters, but call `super().__init__`
    if you do.

    This example implementation puts much of its code in
    height_at.
    """

    def __init__(self, seed: int):
        """
        Initializes this TerrainGenerator with a random
        number generator seed.
        """
        self.rng: random.Random = random.Random(seed)

    @abc.abstractmethod
    def height_at(self, x_pos: int, y_pos: int) -> float:
        """
        For an X and Y coordinate, this generator uses its
        parameters to return a height value.
        """
        ...
