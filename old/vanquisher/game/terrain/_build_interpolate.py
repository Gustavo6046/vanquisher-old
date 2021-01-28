"""CFFI build module for _interpolate.c."""
from cffi import FFI  # type: ignore

C_DEFS = """
float bilinear(int width, float x, float y, float *vals);
"""

ffibuilder = FFI()

ffibuilder.cdef(C_DEFS)

ffibuilder.set_source(
    "vanquisher.game.terrain._interpolate",
    C_DEFS,
    sources=["ext/_interpolate.c"],
)


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
