"""
A few tests concerning the terrain functionality of Vanquisher, primarily generation.
"""

from vanquisher.game.terrain import TerrainChunk, generator as terragen
from vanquisher.game.terrain.generator.peak import PeakTerrainGenerator, Peak


def test_terragen_simple():
    """
    Test a very simple terrain generation
    algorithm and ensure that it generates
    terrain like expected.
    """

    class XYHalfSumGenerator(terragen.TerrainGenerator):
        """
        A very simple terrain generation algorithm,
        where any point's height is half of the sum
        of its X and Y coordinates.
        """

        def height_at(self, x_pos: int, y_pos: int):
            return (x_pos + y_pos) / 2

    my_terrain = TerrainChunk(4)

    my_terrain.generate(XYHalfSumGenerator(0))

    assert my_terrain.get(3, 3) == 3.0
    assert my_terrain.get(3, 2) == 2.5
    assert my_terrain.get(0, 3) == 1.5
    assert my_terrain.get(0, 0) == 0.0
    assert my_terrain[1.5, 1.5] == 1.5

    # For a change, let's try the peak generator.
    # Just to make sure it... makes sense.

    my_peak = Peak(x=5, y=5, height=20, max_radius=5, strength=1.5, lip=1.5, tip=1.5)

    my_terrain.generate(PeakTerrainGenerator(0, 10.0, 0.0, my_peak))

    assert 10.0 < my_terrain[5.0, 5.0] <= 20.0
    assert my_terrain[20.0, 5.0] <= my_terrain[5.0, 5.0]
