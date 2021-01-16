"""
A few tests concerning the terrain functionality of Vanquisher, primarily generation.
"""

from vanquisher.game.terrain import TerrainChunk, generator as terragen


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
