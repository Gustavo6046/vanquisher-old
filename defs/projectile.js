function(G) {
    G.register_object_type({
        name: "projectile",
        attributes: {
            damage: 21
        },
        variables: {
            speed: 30,
            angle: 0
        },
        methods: {
            propel: function (self, angle, speed) {
                self.propel(Math.cos(angle) * speed, Math.sin(angle) * speed);
            }
        },
        callbacks: {
            begin: function (self) {
                self.gravity(0.5);
            },
            end: function (self) {
                self.foreach_radius_objects(5, function(otherObj) {
                    if (otherObj.met.damage_self) {
                        otherObj.met.damage_self(10 + Math.random() * self.att.damage);
                    }
                });
            },
            tick: function (self, timeDelta) {
                // there is friction even in the air lol
                self.m.propel(self.var.angle, self.var.speed * timeDelta);

                // but let's not thrust our projectile too much
                self.var.speed /= Math.pow(1.2, timeDelta);
            }
        }
    });
}