"""Allows using Numba if it is available"""

import typing

try:
    from numba import jit  # type: ignore

except ImportError:
    SUPPORTED = False

else:
    SUPPORTED = True


def maybe_numba_jit(
    *args, **kwargs
) -> typing.Callable[[typing.Callable], typing.Callable]:
    """Safe Numba decorator.

    If Numba is available, wraps a function
    with @numba.jit(*args, **kwargs). Otherwise,
    just returns the unadulterated function instead.
    """

    def _decorator(func: typing.Callable) -> typing.Callable:
        if SUPPORTED:
            return jit(*args, **kwargs)(func)

        # No numba, just return unmodified function
        return func

    return _decorator
