from ursina import *


def update():
    if held_keys['h']:
        for i in scene.entities:
            if i.name in ['entity', 'text', 'button', 'camera', 'raycaster', '_z_plane', 'ui', 'hot_reloader', 'button_list']:
                pass
            else:
                print(i.name)
                if i == mouse.hovered_entity:
                    renderDataPanel(i)

def printEntityData(entity):
    print('Parent Entity : ' + str(entity.parent))
    print('Model : ' + str(entity.model))
    print('Pos x : ' + str(entity.x) + ', Pos y : ' + str(entity.y) + ', Pos z :' + str(entity.z))
    print('Scale x : ' + str(entity.scale[0]) + ', Scale y : ' + str(entity.scale[1]) + ', Scale z : ' + str(entity.scale[2]))
    print('Color : ' + str(entity.color))

def renderDataPanel(entity):
    data_panel = Text(text=('Model : ' + str(entity.model)), background=True, background_color=color.white)
    destroyDataPanel(data_panel=data_panel)

def destroyDataPanel(data_panel):
    destroy(data_panel)


app = Ursina()

test = Entity(model='cube', position=Vec3(1, 2, 3), scale=Vec3(4, 5, 6), collider='cube')

app.run()