"""CFFI build module for _interpolate.c."""
import os

from cffi import FFI

ffibuilder = FFI()

curr_dir = os.path.realpath(os.path.dirname(__file__))

cdef = """
float bilinear(int width, float x, float y, float *vals);
"""

ffibuilder.cdef(cdef)

ffibuilder.set_source(
    "vanquisher.game.terrain._interpolate",
    cdef,
    sources=["ext/_interpolate.c"],
)


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
