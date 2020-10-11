from ursina import *
from panda3d.core import *
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletBoxShape, BulletRigidBodyNode, BulletDebugNode


class GroundBody(Entity):
    def __init__(self, world, **kwargs):
        super().__init__(**kwargs)
        self.shape = BulletPlaneShape(Vec3(0, 1, 0), 0)
        self.node = BulletRigidBodyNode('plane')
        self.node.addShape(self.shape)
        self.np = render.attachNewNode(self.node)
        self.np.setPos(0, -2, 0)
        world.attachRigidBody(self.node)

class BoxBody(Entity):
    def __init__(self, world, **kwargs):
        super().__init__(**kwargs)
        self.shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        self.node = BulletRigidBodyNode('cube')
        self.node.setMass(1.0)
        self.np = render.attachNewNode(self.node)
        self.np.setY(4)
        self.parent = self.np
        world.attachRigidBody(self.node)


app = Ursina()

world = BulletWorld()
world.setGravity(Vec3(0, -9.81, 0))
ground = GroundBody(model='plane', scale=10, color=color.green, world=world)
cube = BoxBody(model='cube', color=color.red, world=world)
window.borderless = False
Sky()
ed = EditorCamera()
ed.rotation = (20, 10, 0)
ed.y = 1
def update():
    if held_keys['space']:
        world.doPhysics(time.dt)


app.run()