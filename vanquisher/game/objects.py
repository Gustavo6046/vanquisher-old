"""
Game objects in the world and their representation,
both for Python and for the object definitions in
JavaScript.
"""

import typing

import uuid
import math

import typing_extensions as typext

from . import vector, object_type, world


class ObjectCallback(typext.Protocol):
    """
    A callback that operates on GameObjectJS,
    usually passed to object iterators.
    """

    def __call__(self, obj_ref: "GameObjectJS"):
        ...


class VariableSetCallback(typext.Protocol):
    """
    A function that allows seting the value of an object
    variable. Passed to 'GameObjectJS.vardo' callbacks.
    """

    def __call__(self, new_value: typing.Any) -> typing.Any:
        ...


class VariableFoundCallback(typext.Protocol):
    """
    A callback that allows setting the value of a variable.

    This one is called when the variable exists and is found.
    """

    def __call__(
        self, value: typing.Any, set_func: VariableSetCallback
    ) -> typing.Optional[typing.Any]:
        ...


class VariableNotFoundCallback(typext.Protocol):
    """
    A callback that allows catching edge cases in variable
    setting.

    This one is called when the variable does not exists
    and/or is not found.
    """

    def __call__(self, set_func: VariableSetCallback) -> typing.Optional[typing.Any]:
        ...


class GameObject:
    """
    A game object.
    """

    def __init__(
        self,
        my_world: "world.World",
        identifier: typing.Optional[uuid.UUID],
        obj_type: str,
        pos: typing.Tuple[float, float],
        height: typing.Optional[float] = None,
        vel_speed: float = 0.0,
        restitution: float = 0.0,
        rolling: float = 0.5,
        horz_speed: typing.Tuple[float, float] = (0, 0),
        friction: float = 0.7,
        num_roll_samples: int = 8,
        sample_distance: float = 0.5,
        gravity: float = 1.0,
    ):
        self.identifier = identifier or uuid.uuid4()

        self.pos: vector.Vec2 = vector.from_tuple2(pos)
        self.horz_speed: vector.Vec2 = vector.from_tuple2(horz_speed)

        self.world = my_world
        self.chunk = self.world.chunk_at_pos(self.pos.as_tuple())

        self.height: float = height if height is not None else self.floor_height
        self.vel_speed: float = vel_speed

        self.restitution: float = restitution
        self.gravity: float = gravity
        self.friction: float = friction
        self.rolling: float = rolling

        self.num_roll_samples: int = num_roll_samples
        self.sample_distance: float = sample_distance

        self._obj_type = obj_type
        self.type: object_type.ObjectType = self.game.object_types.get_type(
            self._obj_type
        )

        self.variables = {}

        for v_name, v_default in self.type.variables.items():
            self.variables[v_name] = v_default

        self.js_wrapper = GameObjectJS(self)

        if "begin" in self.type.callbacks:
            self.type.callbacks["begin"](self.js_wrapper)

    @property
    def floor_height(self):
        """
        The height of the floor at this game object's position.
        """

        return self.chunk.terrain[self.pos.as_tuple()]

    def offset_floor_height(self, off_x: float, off_y: float):
        """
        The height of the floor at a position near that of this game object.
        """

        return self.chunk.terrain[self.pos.x + off_x, self.pos.y + off_y]

    @property
    def game(self):
        """
        The game this object pertains to.
        """

        return self.world.game

    def move(self, offset_x: float, offset_y: float):
        """
        Moves an object horizontally by a certain offset.a

        This is a very rigid move operation, only meant
        if you want that exact offset to be added.

        For more flexible movement, that is more subjected
        to game physics, use `push` instead.
        """

        new_chunk = self.world.chunk_at_pos(self.pos.as_tuple())

        if self.chunk is not new_chunk:
            self.chunk.object_unregister(self)
            new_chunk.object_register(self)

            self.chunk = new_chunk

        self.pos.increment(offset_x, offset_y)

        self.check_physical_state()

    def check_physical_state(self):
        """
        Prevents states that would break the laws of physics,
        such as clipping under the terrain.
        """

        if self.height < self.floor_height:
            self.height = self.floor_height

    def push(self, offset_x: float, offset_y: float):
        """
        Moves  this object horizontally by a certain offset,
        the latter being subjected to physiucs.
        """

        with vector.vec2(offset_x, offset_y) as offset:
            new_height = self.offset_floor_height(offset_x, offset_y)
            slope = new_height - self.floor_height

            if slope > 0:
                offset /= 1 + slope

            elif slope < 0:
                offset *= 1 - slope

            self.move(*offset.as_tuple())

    def get_roll(self):
        """
        Obtains the roll vector of this GaemObject.

        It's the direction of the downward slope,
        obtained by sampling the surrounding areas
        to find the most "downward" way.

        Square roots on sampled heights ensure that
        a general direction is favoured over a single
        narrow steep.
        """

        roll_vec = [0.0, 0.0]

        for sample_index in range(self.num_roll_samples):
            samp_angle = math.pi * sample_index * 2 / self.num_roll_samples

            samp_x = math.cos(samp_angle) * self.sample_distance
            samp_y = math.sin(samp_angle) * self.sample_distance

            samp_height = self.offset_floor_height(samp_x, samp_y)

            roll_vec[0] -= math.sqrt(samp_x * samp_height)
            roll_vec[1] -= math.sqrt(samp_y * samp_height)

        return vector.vec2(*roll_vec)

    def tick(self, time_delta: float):
        """
        Updates the object;
        """

        if self.type.callbacks["tick"]:
            self.type.callbacks["tick"](self)

        self.height += self.vel_speed * time_delta

        with self.horz_speed * time_delta as hspeed:
            self.push(*hspeed.as_tuple())

        if self.height < self.floor_height:
            self.height = self.floor_height

            self.vel_speed = -self.vel_speed * max(0, self.restitution)

            # Apply rolling
            if self.rolling != 0.0:
                with self.get_roll() as roll:
                    with roll * (self.vel_speed * self.friction) as roll:
                        self.horz_speed += roll

        elif self.height > self.floor_height:
            self.vel_speed += self.world.gravity * time_delta

        self.horz_speed *= self.friction ** time_delta

    def destroy(self):
        """
        Destroys this object.
        """

        self.game.object_remove(self)

        if self.type.callbacks["end"]:
            self.type.callbacks["end"](self)

    def __del__(self):
        """
        Ensures vector properties
        are deinitialized.
        """

        if "end" in self.type.callbacks:
            self.type.callbacks["end"](self.js_wrapper)

        self.pos.done()
        self.horz_speed.done()

    def call(self, method_name: str, *args):
        """
        Calls a method defined in the object type
        (that is, defined in JavaScript) directly.
        """
        return self.type.methods[method_name.lower()](self.js_wrapper, *args)


class GameObjectJS:
    """
    A wrapper class whose methods serve as a sort of
    API for JS game object code.

    This is what a JavaScript object definition sees
    when it sees an object.
    """

    def __init__(self, obj: GameObject):
        self.__obj: GameObject = obj

    def var(self, name: str, value: typing.Any = None) -> typing.Optional[typing.Any]:
        """
        JavaScript API shorthand method.

        Gets or sets an object variable.

        Will not raise KeyError, to
        stay consistent with JavaScript object
        behaviour.
        """

        name = name.lower()

        if value is not None:
            self.__obj.variables[name] = value

        return self.__obj.variables.get(name, None)

    def varadd(self, name: str, to_add: typing.Any) -> typing.Any:
        """
        JavaScript API shorthand method.

        Adds to an object variable, in place.

        Assumes a numeric type.

        Will not raise KeyError, to
        stay consistent with JavaScript object
        behaviour.
        """

        name = name.lower()

        self.__obj.variables.setdefault(name, 0)
        self.__obj.variables[name] += to_add

        return self.__obj.variables[name]

    def vard(
        self,
        name: str,
        on_found: VariableFoundCallback,
        on_not_found: typing.Optional[VariableNotFoundCallback] = None,
    ) -> bool:
        """
        JavaScript API shorthand method.

        Looks for an object variable with the name 'name'.
        If it is found, the callback is called with both
        the variable's current value and a set function,
        in that order, and vard returns true. Otherwise,
        the callback is not called, and vard returns false.

        A second, optional callback can also be passed;
        this one will only be called if no variable can be found.
        The set function will still be passed to allow initializing
        the variable (although it is not recommended to do so
        if the variable is not defined among the object definition's
        variables entries).

        Does not raise KeyError.
        """

        name = name.lower()

        def _set(new_value: typing.Any) -> typing.Any:
            """
            Sets the requested variable to a new value.
            Works even if the variable does not exist
            yet, in which case it is created.

            The creation of new variables is not recommended.
            """

            self.__obj.variables[name] = new_value
            return self.__obj.variables[name]

        status = name in self.__obj.variables

        if status:
            val = on_found(self.__obj.variables[name], _set)

        elif on_not_found is not None:
            val = on_not_found(_set)

        if val is not None:
            _set(val)

        return status

    def att(self, name: str) -> typing.Optional[typing.Any]:
        """
        JavaScript API shorthand method.

        Gets an object type attribute.

        Will not raise KeyError, to
        stay consistent with JavaScript object
        behaviour.
        """

        return self.__obj.type.attributes.get(name.lower(), None)

    @property
    def typename(self) -> str:
        """
        Property primarily for access as JavaScript API.

        Obtains the name of this object's type.
        """

        return self.__obj.type.name

    def to_ref(self) -> str:
        """
        Get the 'reference' (stringified UUID) of this game object;
        """
        return str(self.__obj.identifier)

    @property
    def floor_height(self):
        """
        The height of the floor at this game object's position.
        """

        return self.__obj.floor_height

    def push(self, off_x: float, off_y: float):
        """
        'Pushes' an object by an offset.
        Slope physics apply.
        """

        self.__obj.push(off_x, off_y)

    def move(self, off_x: float, off_y: float):
        """
        Moves an object by an exact offset,
        disregarding slope physics.
        """

        self.__obj.move(off_x, off_y)

    def propel(self, vel_x: float, vel_y: float):
        """
        Propels an object's horizontal velocity.
        """

        with vector.vec2(vel_x, vel_y) as thrust:
            self.__obj.horz_speed += thrust

    def destroy(self):
        """
        Destroys this object.
        """

        self.__obj.destroy()

    def iter_radius_objects(self, radius: float, callback: ObjectCallback):
        """
        Iterates on all objects around a radius,
        calling a callback (in ordinary circumstances a
        JavaScript callback) for every object
        found.

        Instead of checking every object in the world, this
        skips far away chunks and only checks chunks that
        have any corner within a radius of this object.
        """

        my_world = self.__obj.world

        # Chunks are square. The diagonal of a square is the largest distance within said square.
        # It is sqrt(2) times the width of the square.
        # So sqrt(2) * world.chunk_width is the maximum we need to add to the search radius
        # to make sure we don't rule out eligible chunks.
        # Also, a little epsilon, just to be extra sure!
        max_chunk_dist_sq = (radius + math.sqrt(2) * my_world.chunk_width + 0.0001) ** 2

        for chunk in my_world.chunks.values():
            # check if chunk overlaps radius
            corner_x, corner_y = (
                (chunk.chunk_pos[0] + 0.5) * my_world.chunk_width,
                (chunk.chunk_pos[1] + 0.5) * my_world.chunk_width,
            )
            distance = (corner_x - self.__obj.pos.x) ** 2 + (
                corner_y - self.__obj.pos.y
            ) ** 2

            if distance > max_chunk_dist_sq:
                continue

            # check if any object is within radius
            for obj in chunk.objects_inside():
                with obj.pos - self.__obj.pos as off_vec:
                    if off_vec.size > radius:
                        continue

                callback(obj.js_wrapper)

    def call(self, method_name: str, *args):
        """
        Calls a method defined in the object type
        (that is, defined in JavaScript) from
        JavaScript. This allows calling am object
        method from another method.
        """
        return self.__obj.call(method_name, *args)
