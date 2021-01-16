"""
Common utility functions to be used throughout Vanquisher.
"""

import typing

RGB = typing.Tuple[float, float, float]


def interpolate(low: float, high: float, alpha: float) -> float:
    """
    Linear interpolatino between two values.
    """

    return (high - low) * alpha + low


def interpolate_color(low: RGB, high: RGB, alpha: float) -> RGB:
    """
    Linear interpolation between two colours. Neat shorthand;
    """

    return (
        interpolate(low[0], high[0], alpha),
        interpolate(low[1], high[1], alpha),
        interpolate(low[2], high[2], alpha),
    )
