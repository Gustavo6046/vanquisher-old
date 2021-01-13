"""
This module is concerned with 2D vector math,
as well as internally the pooling of vectors
for performance purposes.
"""

import typing

import warnings
import math


class Vec2Pool:
    """
    A pool of vectors.

    Used internally to avoid the overhead of rapid creation and
    destruction of vector objects during intense periods of
    calculation.

    Please don't bother.
    """

    def __init__(self, chunk_size: int = 50):
        self.chunk_size: int = chunk_size

        self.pool_free: typing.List[bool] = [True for _ in range(chunk_size)]
        self.pool: typing.List['Vec2'] = []

        self.free: int = chunk_size
        self.size: int = chunk_size
        self.next_free: int = 0

        try:
            self.initialize_pool()

        except NameError:
            # this is probably DEFAULT_POOL.
            #    (if not then something is very wrong
            #     and it's not my fault!)
            pass

    def make(self, init_x: float, init_y: float) -> 'Vec2':
        """
        Allocates and initializes a vector from this pool.
        """

        vec = self.allocate()

        vec.x = init_x
        vec.y = init_y

        vec.update()

        return vec

    def initialize_pool(self):
        """
        Initializes this pool. Always called from __init__, except
        for DEFAULT_POOL where it initially raises NameError due ot
        Vec2 not being defined, and then is called again *after*
        Vec2 is defined.

        Please do not touch this, unless you know EXACTLY what you are doing.
        """

        self.pool: typing.List['Vec2'] = [Vec2(self, i) for i in range(self.chunk_size)]

    def expand(self):
        """
        Expands the actual pool to allow more vectors to reside in it at once.
        """

        start = len(self.pool)

        self.pool.extend(Vec2(self, start + i) for i in range(self.chunk_size))
        self.pool_free.extend(True for _ in range(self.chunk_size))

        self.free += self.chunk_size
        self.size += self.chunk_size

    def _contract(self):
        """
        Contracts the pool forcibly.
        """

        self.pool = self.pool[:self.size - self.chunk_size]
        self.pool_free = self.pool_free[:self.size - self.chunk_size]

        self.size -= self.chunk_size

    def contract(self) -> bool:
        """
        Contracts the pool if there are no allocated vectors in the area to be contracted.
        """

        if self.size <= self.chunk_size:
            # zero is too little
            return False

        for i in range(self.size - self.chunk_size, self.size):
            if not self.pool_free[i]:
                # allocated vectors overlapping area to be contracted, operation denied
                return False

        self._contract()
        return True

    def get(self, index: int) -> typing.Optional['Vec2']:
        """
        'Gets' (allocates) a vector at a specific index in this pool,
        if it is free.
        """

        if not self.pool_free[index]:
            return None

        return self._get(index)

    def _get(self, index: int) -> 'Vec2':
        """
        Returns a vector at a specific index of the pool, while setting it
        to 'allocated' if it wasn't already. This does not check whether
        the vector was already allocated beforehand.
        """

        self.pool_free[index] = False
        self.free -= 1

        return self.pool[index]

    def allocate(self) -> 'Vec2':
        """
        'Allocates' the first vector available and returns it. If there
        are no free slots, it automatically expands the pool.
        """

        if self.free == 0:
            self.next_free = self.size
            self.expand()

        for index in range(self.next_free, self.size):
            if self.pool_free[index]:
                res = self._get(index)

                while not self.pool_free[self.next_free]:
                    self.next_free += 1

                return res

        warnings.warn(RuntimeWarning(
            "VectorContext made space for more vectors, yet still couldn't allocate one"
            " - this might indicate a race condition, expect things to go awry"))

        # fallback - unpooled vector
        return Vec2(None, -1)

    def put(self, index: int):
        """
        'Puts' a vector 'back' into the pool, that is, marks it as free to be
        allocated again. This implies that no further operations are to be done
        within the context the vector was being used right before being discarded.
        """

        if self.pool_free[index]:
            warnings.warn(RuntimeWarning(
                "Vector pool's index {} was already freed".format(index)
            ))
            return

        self.pool[index].reset()
        self.pool_free[index] = True
        self.free += 1

        if self.size > self.chunk_size and self.size - index <= self.chunk_size:
            if self.contract():
                return

        if index < self.next_free:
            self.next_free = index

    def context(
        self,
        vecs: typing.Iterable[typing.Tuple[float, float]] = ((0, 0),)
    ) -> 'VectorContext':
        """
        Allocates several vectors at once.

        vecs can be a list or iterator of (float,float) coordinate
        tuples.

        Useful to quickly get a bunch of vectors for intermediary
        calculation in a "with" block, without nesting a with
        per vector. More vector with less fuss.
        """

        new_vecs = [self.make(*tup) for tup in vecs]

        return VectorContext(new_vecs)


DEFAULT_POOL = Vec2Pool()


class Vec2:
    """
    2D vector. Stores X and Y coordinates.

    I don't need to tell you that this has direction and
    magnitude. If you didn't learn this at high school,
    you learned it in Despicable Me.
    """

    def __init__(self, pool: typing.Optional[Vec2Pool], _index: int):
        self._pool: typing.Optional[Vec2Pool] = pool
        self._index: int = _index

        self.x: float = 0.0
        self.y: float = 0.0

        self.size: float = 0.0

    def done(self):
        """
        Deallocates the vector once you're done using it.
        """

        if self._pool:
            self._pool.put(self._index)

    def reset(self):
        """
        Resets a vector to zero. Used when it is deallocated with done().
        """

        self.x = 0.0
        self.y = 0.0

        self.size = 0.0

    @classmethod
    def make(cls, init_x: float, init_y: float, pool: Vec2Pool = DEFAULT_POOL):
        """
        Gets a vector from the vector pool and initializes it
        with the specified coordinate values.
        """

        return pool.make(init_x, init_y)

    @classmethod
    def from_tuple(cls, tup: typing.Tuple[float, float], pool: Vec2Pool = DEFAULT_POOL):
        """
        Gets a vector from the vector pool and initializes it
        with the coordinate values specified in a (float, float) tuple.
        """

        return cls.make(*tup, pool=pool)

    def __add__(self, other: "Vec2") -> "Vec2":
        """
        Vector addition.
        """

        return self.make(self.x + other.x, self.y + other.y,
                         pool=self._pool or DEFAULT_POOL)

    def __sub__(self, other: "Vec2") -> "Vec2":
        """
        Vector subtraction.
        """

        return self.make(self.x - other.x, self.y - other.y,
                         pool=self._pool or DEFAULT_POOL)

    def __mul__(self, value: float) -> "Vec2":
        """
        Vector-scalar multiplicaiton.
        """

        return self.make(self.x * value, self.y * value,
                         pool=self._pool or DEFAULT_POOL)

    def __truediv__(self, value: float) -> "Vec2":
        """
        Vector-scalar division.
        """

        return self.make(self.x / value, self.y / value,
                         pool=self._pool or DEFAULT_POOL)

    def __iadd__(self, other: "Vec2"):
        """
        In-place vector addition.
        """

        self.x += other.x
        self.y += other.y

        self.update()

        return self

    def __isub__(self, other: "Vec2"):
        """
        In-place vector subtraction.
        """

        self.x -= other.x
        self.y -= other.y

        self.update()

        return self

    def __imul__(self, value: float):
        """
        In-place vector-scalar multiplication.
        """

        self.x *= value
        self.y *= value

        self.update()

        return self

    def __itruediv__(self, value: float):
        """
        In-place vector-scalar division.
        """

        self.x /= value
        self.y /= value

        self.update()

        return self

    def _compute_size(self) -> float:
        """
        Calculates the size of the vector.
        Don't use; is called automatically when the
        vector is changed.
        """

        return math.sqrt(self.x ** 2 + self.y ** 2)

    def update(self):
        """
        Updates the size of the vector.
        Don't bother; is called automatically when
        the vector is changed.
        """

        self.size = self._compute_size()

    def unit(self) -> "Vec2":
        """
        Returns a vector of same orientation and
        unit magnitude (length 1).

        Useful for operations that concern orientation
        or direction.
        """

        return self / self.size

    def unitify(self):
        """
        Changes this vector's length to 1.0 while
        preserving the orientation.

        Useful for operations that concern orientation
        or direction.
        """

        self /= self.size

    def dot(self, other: "Vec2") -> float:
        """
        Calculates the dot product, or scalar
        product, of this and another vector.
        """

        return self.x * other.x + self.y * other.y

    def unit_dot(self, other: "Vec2") -> float:
        """
        Calculates the dot product, or scalar
        product, of this and another vector,
        then divides by the compounded magnitude
        of both.

        `unit_dot` is the same as `dot` when both
        vectors are already unit vectors (have a
        length of 1.0).

        This is useful, for instance, when calculating
        how "similar" the orientatino of two vectors is.
        """

        return (self.x * other.x + self.y * other.y) / self.size / other.size

    def as_tuple(self):
        """
        Returns the float,float tuple of this vector's coordinates.
        """

        return (self.x, self.y)

    def increment(self, add_x: float = 1.0, add_y: float = 0.0):
        """
        Increments this vector by X and Y coordinates, rather than
        by another vector. In practice, this is also vector
        addition.
        """

        self.x += add_x
        self.y += add_y

    def add_tuple(self, tup: typing.Tuple[float, float]):
        """
        Increments this vector by the X and Y coordinates specified
        in this (float,float) tuple. In practice, this is also
        vector addition.
        """

        self.x += tup[0]
        self.y += tup[1]

    def __repr__(self):
        """
        Internal human-readable representation of this vector.
        Slightly verbose.
        """

        return 'Vec2({0.x},{0.y},|{0.size}|)#{0._index}'.format(self)

    def __str__(self):
        """
        Human-readable string representation of this vector. Succint.
        """

        return '<{0.x},{0.y}>'.format(self)

    def __enter__(self):
        """
        Using a 'with' statement on this vector  automatically calls
        done() on it after the end of the with block.
        """

        return self

    def __exit__(self, _1, _2, _3):
        self.done()


DEFAULT_POOL.initialize_pool()


def vec2(init_x: float, init_y: float) -> Vec2:
    """
    A shorthand to quickly make a 2D vector.
    Try using this with a 'with' block to
    avoid calling done manually or losing the
    reference to the vector after using it.
    """

    return Vec2.make(init_x, init_y, pool=DEFAULT_POOL)


def from_tuple2(tup: typing.Tuple[float, float]) -> Vec2:
    """
    A shorthand to quickly make a 2D vector
    from a (float,float) coordinate tuple.
    Try using this with a 'with' block to
    avoid calling done manually or losing the
    reference to the vector after using it.
    """

    return Vec2.from_tuple(tup, pool=DEFAULT_POOL)


class VectorContext:
    """
    A context that quickly allocates multiple vectors,
    often intermediary values, and throws them away after
    a with block.
    """

    def __init__(self, *vecs):
        self._vecs = list(vecs)

    def __enter__(self):
        return self._vecs

    def __exit__(self, _1, _2, _3):
        for vec in self._vecs:
            vec.done()
