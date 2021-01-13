import math

import vanquisher.game.vector as vc


def test_indices():
    pool = vc.Vec2Pool()

    v1 = pool.make(2, 2)
    v2 = pool.make(1, 2)

    assert v1._index == 0
    assert v2._index == 1

    v3 = v1 + v2

    assert v3._index == 2
    assert v3.x == 3
    assert v3.y == 4
    assert v3.size == 5

    v1.done()
    v2.done()
    v3.done()

    assert pool.free == pool.size


def test_vector_arithmetics():
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
        # I promise I'll find something more convenient than the 'with block' gizmos someday.

    assert pos.as_tuple() == (25, 20)

    pos.done()
    vel.done()

    assert pool.free == pool.size
