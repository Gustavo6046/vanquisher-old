"""
Tests concerned with object types and the JavaScript API in general.
"""

import vanquisher.game as gamepkg


def test_load_object_1():
    """
    A simple test focused on loading simple
    info, like attributes, and ensuring
    things are overall loaded properly.
    """

    js_module = """
    function (G) {
        G.register_object_type({
            name: 'my_type',
            attributes: {
                'a': 42,
                'b': 'Hello World!',
                'c': [2, 3, 4]
            }
        });
    }
    """

    game = gamepkg.Game()

    game.object_types.load_module(js_module)

    assert len(game.object_types.object_types) == 1

    my_new_type = game.object_types.get_type("my_type")

    # ensure sane loading
    assert my_new_type.name == "my_type"
    assert len(my_new_type.attributes) == 3
    assert len(my_new_type.variables) == 0
    assert len(my_new_type.methods) == 0
    assert len(my_new_type.callbacks) == 0
    assert my_new_type.inherit is None

    # check those attributes
    assert my_new_type.attributes["a"] == 42
    assert my_new_type.attributes["b"] == "Hello World!"
    assert len(my_new_type.attributes["c"]) == 3
    assert tuple(my_new_type.attributes["c"]) == (2, 3, 4)


def test_load_object_2():
    """
    Tests the initialization of variables
    in created game_objects, as well as methods
    """

    js_module = """
    function (G) {
        G.register_object_type({
            name: 'my_type',
            variables: {
                cookies: 10
            },
            methods: {
                eat_cookie: function(self) {
                    self.varadd('cookies', -1);
                },

                make_cookie: function(self) {
                    self.varadd('cookies', 1);
                },
            },
            callbacks: {
                begin: function(self) {
                    // just to make sure; you never quite have enough!
                    self.var('cookies', self.var('cookies') + 5);
                },
            },
        });
    }
    """

    game = gamepkg.Game()

    game.object_types.load_module(js_module)

    assert len(game.object_types.object_types) == 1

    my_new_type = game.object_types.get_type("my_type")

    # ensure sane loading
    assert my_new_type.name == "my_type"
    assert len(my_new_type.attributes) == 0
    assert len(my_new_type.variables) == 1
    assert len(my_new_type.methods) == 2
    assert len(my_new_type.callbacks) == 1
    assert my_new_type.inherit is None

    # check all vars and methods were loaded
    assert set(my_new_type.variables.keys()) == {"cookies"}
    assert set(my_new_type.methods.keys()) == {"eat_cookie", "make_cookie"}
    assert set(my_new_type.callbacks.keys()) == {"begin"}
    assert my_new_type.variables["cookies"] == 10  # the default, before begin callback

    # instantiate an object of that kind
    cookie_object = game.object_create("my_type", (5, 7))

    # ensure sane creatoin
    assert cookie_object.pos.x == 5
    assert cookie_object.pos.y == 7
    assert cookie_object.vel_speed == 0.0
    assert len(list(cookie_object.variables)) == 1

    # check if begin callback updated cookies
    # (begin callback should've added 5 to the default of 10)
    assert cookie_object.variables["cookies"] == 15.0

    # try the methods
    cookie_object.call("make_cookie")
    assert cookie_object.variables["cookies"] == 16.0  # one more!

    for _ in range(9):
        cookie_object.call("eat_cookie")  # yum!
    assert cookie_object.variables["cookies"] == 7.0


def test_load_object_3():
    """
    Tests object type inheritance (i.e. definition mixin).
    """

    js_module = """
    function (G) {
        G.register_object_type({
            name: 'animal',
            methods: {
                get_noise: function(self) {
                    throw new Error("This animal does not have a noise!");
                },

                do_noise: function(self) {
                    return (
                        "The " + self.att('animal_name') + 
                        " goes '" + self.call('get_noise') + "!'"
                    );
                },
            },
        });

        G.register_object_type({
            name: 'duck',
            inherit: ['animal'],
            attributes: {
                animal_name: "Duck",
            },
            methods: {
                get_noise: function(self) {
                    return 'Quack'
                }
            },
        });

        G.register_object_type({
            name: 'cow',
            inherit: ['animal'],
            attributes: {
                animal_name: "Cow",
            },
            methods: {
                get_noise: function(self) {
                    return 'Moo'
                }
            },
        });
    }
    """

    game = gamepkg.Game()

    game.object_types.load_module(js_module)

    assert len(game.object_types.object_types) == 3

    animal_t = game.object_types.get_type("animal")
    duck_t = game.object_types.get_type("duck")
    cow_t = game.object_types.get_type("cow")

    # ensure sane loading
    assert animal_t.name == "animal"
    assert duck_t.name == "duck"
    assert cow_t.name == "cow"

    assert animal_t.inherit is None
    assert duck_t.inherit is not None
    assert cow_t.inherit is not None

    assert len(duck_t.inherit) == 1
    assert len(cow_t.inherit) == 1
    assert set(duck_t.inherit) & set(cow_t.inherit) == {"animal"}

    assert len(duck_t.attributes) == 1
    assert len(cow_t.attributes) == 1
    assert len(animal_t.attributes) == 0

    assert len(duck_t.methods) == 2
    assert len(cow_t.methods) == 2
    assert len(animal_t.methods) == 2

    # try the noises
    my_duck = game.object_create("duck", (0, 0))
    my_cow = game.object_create("cow", (0, 0))

    assert my_duck.call("do_noise") == "The Duck goes 'Quack!'"
    assert my_cow.call("do_noise") == "The Cow goes 'Moo!'"
