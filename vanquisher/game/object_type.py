"""
Game object types from JavaScript and some nuances
on their interaction with the playsim in Python.
"""

import typing
import uuid
import warnings

import typing_extensions as typext
import js2py

from . import objects, game


class ObjectTypeMethod(typext.Protocol):
    """
    A callable, usually defined in JavaScript, that
    defines a method for an object type.
    """

    def __call__(self, object_self: "objects.GameObjectJS", *args: typing.Any) -> typing.Any: ...


class TypeDefinitionObject(typext.Protocol):
    """
    An object that is passed to ctx.register_object_type
    whenever an object type is to be registered from
    JavaScript extension code.
    """

    @typing.overload
    def __getitem__(self, key: typing.Literal['name']) -> str: ...

    @typing.overload
    def __getitem__(self, key: typing.Literal['inherit']) \
        -> typing.Optional[typing.Iterable[str]]: ...

    @typing.overload
    def __getitem__(self, key: typing.Literal['methods']) \
        -> typing.Mapping[str, ObjectTypeMethod]: ...

    @typing.overload
    def __getitem__(self, key: typing.Literal['callbacks']) \
        -> typing.Mapping[str, ObjectTypeMethod]: ...

    @typing.overload
    def __getitem__(self, key: typing.Literal['attributes']) \
        -> typing.Mapping[str, typing.Any]: ...

    @typing.overload
    def __getitem__(self, key: typing.Literal['variables']) \
        -> typing.Mapping[str, typing.Any]: ...

    def __getitem__(self, key: str) -> typing.Any: ...


class GameContextJS:
    """
    The game context, as seen from a JavaScript object definition.
    This object is passed to the function that returns the defiintion.
    In JS call it something short, like maybe just G.
    """

    def __init__(self, my_game: "game.Game"):
        self.__game = my_game

    @property
    def def_context(self) -> 'ObjectTypeContext':
        """
        The ObjectTypeContext this GameContextJS indirectly pertains to.
        """
        return self.__game.object_types

    def ref(self, ident: str) -> typing.Optional["objects.GameObjectJS"]:
        """
        Resolves an object identifier UUID string into its
        corresopnding GameObjectJS.
        """

        uid = uuid.UUID(ident)
        obj: typing.Optional[objects.GameObject] = self.__game.objects.get(uid, None)

        if obj:
            return obj.js_wrapper

        return None

    def register_object_type(self, type_defs: TypeDefinitionObject):
        """
        Registers an object type to this game
        context via an object type definition object.
        This is meant to be called from JS.
        """

        otype = ObjectType(self.def_context, type_defs)

        self.def_context.register_type(otype)

    def iter_all_objects(self, callback: objects.ObjectCallback):
        """
        Iterates on all objects in the game. For each object,
        calls the callback (in ordinary circumstances a JS
        function).
        """

        for obj in self.__game.objects.values():
            callback(obj.js_wrapper)


class ObjectTypeContext:
    """
    A context that holds object types for a specific
    game.
    """

    def __init__(self, my_game: "game.Game"):
        self.game = my_game
        self.js_context = GameContextJS(self.game)
        self.object_types: typing.Dict[str, "ObjectType"] = {}

    def register_type(self, obj_type: 'ObjectType'):
        """
        Registers an object type to this ObjectTypeContext.
        """

        self.object_types[obj_type.name] = obj_type

    def load_module(self, source_js: str):
        """
        Loads an object type from a string of JS source code.
        """

        js2py.eval_js(source_js)(self.js_context)

    def get_type(self, type_name: str) -> "ObjectType":
        """
        Fetches an ObjectType by its name, case insensitively.
        """

        return self.object_types[type_name.lower()]


class ObjectType:
    """
    An object type.

    Holds a bunch of useful information, particularly metadata,
    defaults and functions, related to an object type defined
    in JavaScript.
    """

    def __init__(self, ctx: ObjectTypeContext, object_type_js: TypeDefinitionObject):
        self.name = str(object_type_js['name']).lower()

        self.inherit: typing.Optional[typing.List[str]]

        if 'inherit' in object_type_js:
            self.inherit = [str(x).lower() for x in object_type_js['inherit']]

        else:
            self.inherit = None

        self.methods: typing.Dict[str, typing.Callable] = {}
        self.attributes: typing.Dict[str, typing.Optional[typing.Union[str, int, float]]] = {}
        self.variables: typing.Dict[str, typing.Optional[typing.Union[str, int, float]]] = {}
        self.callbacks: typing.Dict[str, typing.Callable] = {}

        if 'methods' in object_type_js:
            d_methods = object_type_js['methods']

            for method_name in d_methods:
                method_func = d_methods[method_name]
                self.methods[method_name.lower()] = method_func

        if 'attributes' in object_type_js:
            d_attrs = object_type_js['attributes']

            for attr_name in d_attrs:
                attr_val = d_attrs[attr_name]
                self.attributes[attr_name.lower()] = attr_val

        if 'variables' in object_type_js:
            d_vars = object_type_js['variables']

            for var_name in d_vars:
                var_default = d_vars[var_name]
                self.variables[var_name.lower()] = var_default

        if 'callbacks' in object_type_js:
            d_callbacks = object_type_js['callbacks']

            for cb_name in d_callbacks:
                cb_func = d_callbacks[cb_name]
                self.callbacks[cb_name.lower()] = cb_func

        if self.inherit:
            for inherit_name in self.inherit:
                self.check_mixin(ctx, inherit_name)

    def check_mixin(self, ctx: ObjectTypeContext, maybe_mixin_type: str) -> bool:
        """
        Tries to inherit a mixin, by fetching it
        by its type name if possible. Returns
        True if successful, False (and a UserWarning)
        otherwise.
        """

        try:
            inherited = ctx.get_type(maybe_mixin_type.lower())

        except KeyError:
            warnings.warn(UserWarning("Could not find inherit"))
            return False

        else:
            self.mixin(inherited)
            return True

    def mixin(self, mixin_type: 'ObjectType'):
        """
        Mixes the methods, attributes and variables of another
        type into this type, as long as they don't already exist.
        """

        for method_name, method_func in mixin_type.methods.items():
            if method_name not in self.methods:
                self.methods[method_name] = method_func

        for attribute_name, attribute_val in mixin_type.attributes.items():
            if attribute_name not in self.attributes:
                self.attributes[attribute_name] = attribute_val

        for variable_name, variable_default in mixin_type.attributes.items():
            if variable_name not in self.variables:
                self.variables[variable_name] = variable_default
