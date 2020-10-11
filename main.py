from ursina import *

app = Ursina()

window.fullscreen = False
window.title = 'Ursina GUI'
window.borderless = False
window.windowed_size = LVector2f(1500, 1200)
print(window.windowed_size)


_window_size_x = window.size[0]
_window_size_y = window.size[1]
_window_scale_x = 14.5 # ~
_window_scale_y = 8.1 # ~

panel_right = Entity(model='quad', scale=Vec3((_window_scale_x / 2), _window_scale_y, 1), position=Vec3((_window_scale_x / 4), (_window_scale_y / 4), 0))
button = Button(parent=panel_right, text='Play', color=color.red, scale=Vec3(2, 2, 2), position=Vec3(panel_right.x, panel_right.y, 1))

app.run()