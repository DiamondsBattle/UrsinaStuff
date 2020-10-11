from ursina import *
from ursina.scripts.grid_layout import grid_layout

app = Ursina()

def update():
    if held_keys['space']:
        scene.paused = not key.paused


center = Entity()

grid_layout(center.children)

app.run()