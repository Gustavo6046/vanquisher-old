"""
The framebuffer is responsible for storing the
colour and Z-buffer values of each pixel. This
is the common interface between Vanquisher's
renderer and backends like Pygame.

A few common backends are already implemented
under framebuffer.pygame, etc., but
"""

import abc
import typing


class Framebuffer:
    """
    A Framebuffer interface.

    This uses abc, instead of typing.Protocol,
    as it is an actual target to be implemented,
    rather than .
    """
