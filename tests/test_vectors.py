"""
Test cases concerned with the vectors
that Vanquisher provide.
"""

import math

import vanquisher.game.vector as vc


def test_indices():
    """
    Tests that vector pooling works well.
    """

    pool = vc.Vec2Pool()

    vec_1 = pool.make(2, 2)
    vec_2 = pool.make(1, 2)

    assert vec_1._index == 0
    assert vec_2._index == 1

    vec_3 = vec_1 + vec_2

    assert vec_3._index == 2
    assert vec_3.x == 3
    assert vec_3.y == 4
    assert vec_3.size == 5

    vec_1.done()
    vec_2.done()
    vec_3.done()

    assert pool.free == pool.size


def test_vector_arithmetics():
    """
    Tests that vector arithmetics work well.
    """

    pool = vc.Vec2Pool()

    pos = pool.make(5, 0)
    vel = pool.make(2, 2)

    assert pos is not None
    assert vel is not None

    assert vel.size == math.sqrt(
        8
    )  # I know that it simplifies to 2*sqrt(2), and I don't care.

    pos += vel

    assert pos._index == 0  # still the same

    assert pos.as_tuple() == (7, 2)

    with vel * 9 as accum_vel:
        pos += accum_vel  # nine more timesteps, for a total of ten
        # I promise I'll find something more convenient than the
        # 'with block' gimmick someday.

    assert pos.as_tuple() == (25, 20)

    pos.done()
    vel.done()

    assert pool.free == pool.size
