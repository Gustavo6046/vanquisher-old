"""
This module concerns with the behaviour of the world,
its basic structure, and how it contains and integrates
the objects that live and the terrain that lay in it.
"""

import math
import typing
import uuid

from . import terrain, vector

if typing.TYPE_CHECKING:
    from . import Game, objects
    from .terrain.generator import TerrainGenerator


class Chunk:
    """
    A chunk; a piece of the world that was generated ans
    is loaded in memory.
    """

    def __init__(self, world: "World", chunk_pos: typing.Tuple[int, int]):
        """
        Initializes this chunk, with an initial, ungenerated TerrainChunk.
        This does not generate the terrain; World does that automatically
        if it has a generator set when this chunk is generated.
        """
        self.world = world
        self.chunk_pos = chunk_pos
        self.width = self.world.chunk_width
        self.world_pos = (
            self.chunk_pos[0] * self.width,
            self.chunk_pos[1] * self.width,
        )
        self.terrain = terrain.TerrainChunk(self.width)

        self.objects_in_chunk: typing.Set[uuid.UUID] = set()

    def __getitem__(self, coords: typing.Tuple[float, float]) -> float:
        """Gets terrain at a world-space point.

        Unlike TerrainChunk, this accounts for world-space, not
        for the coordinates within a chunk. (Chunk-space is the
        coordinates of a chunk's position with respect to the
        others, not of positions within said chunk.)
        """
        coord_x, coord_y = coords

        terra_pos = (
            coord_x - self.world_pos[0],
            coord_y - self.world_pos[1],
        )

        return self.terrain[terra_pos]

    def game(self):
        """
        Fetches the game whose world this chunk belongs to.
        """
        return self.world.game

    def objects_inside(self) -> typing.Generator["objects.GameObject", None, None]:
        """
        Iterates on all the objects in this chunk.
        """

        for obj_id in self.objects_in_chunk:
            yield self.game().objects[obj_id]

    def object_register(self, obj: "objects.GameObject"):
        """
        Regsiters an object to this chunk.
        """

        self.objects_in_chunk.add(obj.identifier)

    def object_unregister(self, obj: "objects.GameObject"):
        """
        Unregsiters an object from this chunk.
        """

        self.objects_in_chunk.remove(obj.identifier)


class World:
    """The world in which objects interact to the terrain and each other."""

    def __init__(
        self,
        my_game: "Game",
        terrain_generator: typing.Optional["TerrainGenerator"] = None,
        chunk_width: int = 32,
        base_height: float = 32.0,
        gravity: float = -4.0,
    ):
        """World initialization.

        Creates an empty world, with a few parameters and
        an empty list of chunks, and optionally sets its
        generator too.
        """
        self.game = my_game
        self.chunk_width = chunk_width
        self.base_height = base_height
        self.gravity = gravity

        self.terrain_generator = terrain_generator
        self.chunks: typing.Dict[typing.Tuple[int, int], Chunk] = {}

    def set_terrain_generator(self, generator: "TerrainGenerator"):
        """Sets the terrain generator this world should use to generate new chunks."""
        self.terrain_generator = generator

    def get_chunk(self, chunk_pos: typing.Tuple[int, int]) -> Chunk:
        """Gets a chunk at a chunk-space position."""
        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos]

        return self.make_chunk(*chunk_pos)

    def chunk_at_pos(
        self, pos: typing.Union[vector.Vec2, typing.Tuple[float, float]]
    ) -> Chunk:
        """Gets a chunk at a world-space position."""
        if isinstance(pos, vector.Vec2):
            pos_x, pos_y = pos.as_tuple()

        else:
            pos_x, pos_y = pos

        return self.get_chunk(
            (math.floor(pos_x / self.chunk_width), math.floor(pos_y / self.chunk_width))
        )

    def object_register(self, obj: "objects.GameObject"):
        """Registers a game object to the chunk it is in.

        Use `Game.oobject_register` instead. That affects the
        whole playsim.
        """
        chunk = self.chunk_at_pos(obj.pos.as_tuple())
        chunk.object_register(obj)

    def object_unregister(self, obj: "objects.GameObject"):
        """Unregisters a game object from the chunk it was in.

        Use `Game.oobject_unregister` instead. That affects the
        whole playsim.
        """
        chunk = self.chunk_at_pos(obj.pos.as_tuple())
        chunk.object_unregister(obj)

    def make_chunk(self, chunk_x: int, chunk_y: int) -> Chunk:
        """Initializes and generates a chunk at a specified chunk-space position."""
        new_chunk = Chunk(self, (chunk_x, chunk_y))
        off_x = chunk_x * self.chunk_width
        off_y = chunk_y * self.chunk_width

        if self.terrain_generator:
            new_chunk.terrain.generate(self.terrain_generator, (off_x, off_y))

        self.chunks[chunk_x, chunk_y] = new_chunk

        return new_chunk

    def update_objects(self, time_delta: float):
        """Updates all objects in this world."""
        for obj in self.game.objects.values():
            obj.tick(time_delta)
