"""Object-world interaction test suite.

This small test unit regards the presence of objects
in the world and the latter's partitioning into chunks,
including things like object iterators and chunk lookups.
"""

from vanquisher.game import Game


def test_object_radius():
    """Test that objects can find nearby objects even across chunks."""

    # Placeholder types.
    js_module = """
    function (G) {
        G.register_object_type({
            name: 'thing',

            methods: {
                countAround: function (self, radius, maybeType) {
                    if (!maybeType) {
                        maybeType = null;
                    }

                    let count = 0;

                    self.iter_radius_objects(function (obj) { count++; }, radius, maybeType);

                    return count;
                },
            },
        });

        G.register_object_type({
            name: 'cake'
        });
    }
    """

    game = Game()
    game.object_types.load_module(js_module)

    # Add 4 things, one of them the pivot

    pivot = game.object_create('thing', (0, 0), 0)

    game.object_create('thing', (38, 0), 0)
    game.object_create('thing', (-50, 0), 0)
    game.object_create('thing', (-17, 36), 0)

    num_things = 4

    assert len(game.objects) == num_things

    # Add 3 cakes, of special interest later on

    game.object_create('cake', (20, 0))
    game.object_create('cake', (0, 15))
    game.object_create('cake', (75, 75))

    num_cakes = 3

    assert len(game.objects) == num_things + num_cakes

    # Find all things in a radius of 45

    assert pivot.call('countAround',  1000.0,  False)   == 7 # everything
    assert pivot.call('countAround',  45.0,    False)   == 5 # close things
    assert pivot.call('countAround',  1000.0,  'cake')  == 3 # every cake
    assert pivot.call('countAround',  45.0,    'cake')  == 2 # close cakes

    # Ensure chunk creation is consistent with the
    # positions passed

    num_chunks_pred = len(game.world.chunks)

    chunk_set = set()

    chunk_set.add(game.world.chunk_at_pos((38, 0)))
    chunk_set.add(game.world.chunk_at_pos((-50, 0)))
    chunk_set.add(game.world.chunk_at_pos((-17, 36)))
    chunk_set.add(game.world.chunk_at_pos((20, 0)))
    chunk_set.add(game.world.chunk_at_pos((0, 15)))
    chunk_set.add(game.world.chunk_at_pos((75, 75)))

    assert len(game.world.chunks) == len(chunk_set) == num_chunks_pred
