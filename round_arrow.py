from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController as FPS

class RoundArrow(Entity):
    def __init__(self, **kwargs):
        self.cone = Draggable(lock_x=True, lock_z=True, model='cone', color=color.black)
        self.cylinder = Draggable(lock_x=True, lock_z=True, model='cylinder', position=Vec3(0, -1, 0), scale=Vec3(0.1, 1.2, 0.1))
        super().__init__(**kwargs)


if __name__ == '__main__':
    app = Ursina()

    arrow = RoundArrow()

    app.run()