from ursina import *
from window_panel import WindowPanel
from move_gizmo import MoveGizmo
from dropdown_menu import DropdownMenu, DropdownMenuButton, DropdownMenuSeparator

import webbrowser as wb


class EditorIcon(Draggable):
    def __init__(self, **kwargs):
        super().__init__(
            parent=scene,
            world_scale=.25,
            always_on_top=True,
            model='sphere',
            color=color.black,
            plane_direction=(0, 1, 0),
            require_key='g',
        )
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.text = 'entity'
        self.text_entity.y = 1
        self.text_entity.ignore = True
        self.text_entity.scale *= .5
        self.text_entity.enabled = self.scene_editor.show_names
        self.dot = Entity(parent=self, ignore=True, model='sphere', scale=.85, color=color.white)
        self.help_text = Text(x=-.5 * camera.aspect_ratio,
                              text='[g]:move\n[e]:scale\n[y]:move up/down\n[F2]:rename selected')

    def drag(self):
        self.always_on_top = False
        if not self.scene_editor.selection and not held_keys['alt']:  # nothing selected, so just move this one
            self.scene_editor.selection.append(self)

        for icon in self.scene_editor.selection:
            icon.entity.original_parent = icon.entity.parent
            icon.entity.world_parent = self

    def drop(self):
        self.always_on_top = True
        for icon in self.scene_editor.selection:
            icon.entity.world_parent = icon.entity.original_parent


class AssetMenu(ButtonList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scrollable = self.add_script(Scrollable(min=self.y, max=len(self.button_dict) * self.button_height))

    def on_enable(self):
        self.scene_editor.editor_camera.ignore = True
        self.y = mouse.y

    def on_disable(self):
        self.scene_editor.editor_camera.ignore = False

    def input(self, key):
        super().input(key)
        if key == 'left mouse down':
            if not mouse.hovered_entity or not mouse.hovered_entity.has_ancestor(self):
                self.enabled = False


class SelectionBox(Entity):
    def input(self, key):
        if key == 'left mouse down' and not held_keys['g']:
            self.position = mouse.position
            self.scale = .001
            self.visible = True
            self.mode = 'new'
            if held_keys['shift']:
                self.mode = 'add'
            if held_keys['alt']:
                self.mode = 'subtract'

        if key == 'left mouse up':
            self.visible = False

            if self.scale_x < 0:
                self.x += self.scale_x
                self.scale_x = abs(self.scale_x)
            if self.scale_y < 0:
                self.y += self.scale_y
                self.scale_y = abs(self.scale_y)

            if self.scale_x < .1 or self.scale_y < .1 or held_keys['g']:
                return

            if self.mode == 'new':
                self.scene_editor.clear_selection()

            for icon in self.scene_editor.editor_icons:

                pos = icon.screen_position
                if self.x < pos.x < self.x + abs(self.scale_x) and pos.y > self.y and pos.y < self.y + abs(
                        self.scale_y):
                    if self.mode != 'subtract' and not icon in self.scene_editor.selection:
                        self.scene_editor.selection.append(icon)

                    elif icon in self.scene_editor.selection:
                        self.scene_editor.selection.remove(icon)

            self.scene_editor.render_selection()
            self.mode = 'new'

    def update(self):
        if mouse.left:
            if mouse.x == mouse.start_x and mouse.y == mouse.start_y:
                return
            # if self.dragging:
            self.scale_x = mouse.x - self.x
            self.scale_y = mouse.y - self.y


class SceneEditor(Entity):
    def __init__(self):
        super().__init__()
        self.world_grid = Entity(parent=self, model=Plane((32, 32), mode='line'), scale=32, color=color.white33,
                                 collider='box', collision=False)

        self.cursor_3d = Entity(parent=self, model=Mesh(vertices=(0, 0, 0), mode='point', thickness=10),
                                color=color.pink, visible=False)
        line_model = Mesh(vertices=((-1, 0, 0), (1, 0, 0)), mode='line', thickness=2)
        self.cursor_3d.rulers = (
            Entity(parent=self.cursor_3d, model=copy(line_model), scale_x=999, color=color.magenta, enabled=False,
                   add_to_scene_entities=False),
            Entity(parent=self.cursor_3d, model=copy(line_model), scale_x=999, color=color.yellow, rotation_z=90,
                   enabled=False, add_to_scene_entities=False),
            Entity(parent=self.cursor_3d, model=copy(line_model), scale_x=999, color=color.cyan, rotation_y=90,
                   enabled=False, add_to_scene_entities=False),
        )
        self.editor_camera = EditorCamera()
        # self.cursor = Cursor()
        # mouse.visible = False

        self.entities = list()
        self.editor_icon_parent = Entity()
        self.editor_icons = list()
        self.selection = list()
        self.selection_text = Text(position=window.top_left, origin=(-.5, .5), text='Selection:')
        self.selection_box = SelectionBox(scene_editor=self, parent=camera.ui, model=Quad(0, mode='line'),
                                          origin=(-.5, -.5, 0), scale=(0, 0, 1), color=color.white33)

        self.duplicate_dragger = Draggable(parent=scene, model='plane', plane_direction=(0, 1, 0), enabled=False)

        def drop(self=self):
            for e in self.duplicate_dragger.children:
                e.world_parent = e.original_parent
            self.duplicate_dragger.enabled = False

        self.duplicate_dragger.drop = drop

        self.models = []
        self.models = [e.stem for e in application.internal_models_compressed_folder.glob('**/*.ursinamesh')]
        for file_type in ('.bam', '.obj', '.ursinamesh'):
            self.models += [e.stem for e in application.asset_folder.glob(f'**/*.{file_type}') if not 'animation' in e]
        self.model_menu = AssetMenu(
            button_dict={key: Func(self.set_attr_for_selected, 'model', key) for key in self.models}, scene_editor=self,
            enabled=False)

        self.textures = []
        for file_type in ('.png', '.jpg', '.gif', '.psd'):
            self.textures += [e.stem for e in application.asset_folder.glob(f'**/*{file_type}') if
                              not e.stem in self.textures]
            self.textures += [e.stem for e in application.internal_textures_folder.glob(f'**/*{file_type}') if
                              not e.stem in self.textures]
            self.textures += [e for e in ('white_cube', 'brick') if not e in self.textures]
        self.texture_menu = AssetMenu(
            button_dict={key: Func(self.set_attr_for_selected, 'texture', key) for key in self.textures},
            scene_editor=self, enabled=False)
        self.rename_window = WindowPanel(
            title='Rename',
            content=(
                InputField(name='name'),
                Button(text='Rename', color=color.azure, on_click=self.rename_selected),
            ),
            enabled=False,
            popup=True,
        )
        self.show_names = False

        self.load('test')

        self.loadStuff()

        self.top_menu = DropdownMenu('Menu', buttons=(
            DropdownMenuSeparator(),
            DropdownMenu('Entity', buttons=(
                DropdownMenuButton('New', on_click=self.newEntity),
                DropdownMenuSeparator(),
                DropdownMenu('Texture', buttons=self.textures_buttons),
                DropdownMenu('Model', buttons=self.models_buttons),
                DropdownMenu('Shader', buttons=(
                    DropdownMenuButton('Custom'), # add FileBrowser
                    DropdownMenuButton('None')
                )),
                DropdownMenu('Animation', buttons=(
                    DropdownMenuButton('Custom'), # add FileBrowser
                    DropdownMenuButton('None')
                )),
                DropdownMenuSeparator(),
                DropdownMenuButton('Scale', on_click=self.scale),
                DropdownMenu('Reposition Axis', buttons=(
                    DropdownMenuButton('X', on_click=Func(self.xPositionInput, 'selection', self.selection)),
                    DropdownMenuButton('Y', on_click=Func(self.yPositionInput, 'selection', self.selection)),
                    DropdownMenuButton('Z', on_click=Func(self.zPositionInput, 'selection', self.selection)),
                )),
                DropdownMenuButton('Duplicate', on_click=Func(self.duplicate, 'entity', self.selection)),
                DropdownMenuButton('Destroy', on_click=self.destroySelection),
                DropdownMenuSeparator(),
                DropdownMenu('Help', buttons=(
                    DropdownMenuButton('Tutorial', on_click=openUrsinaForDummiesWebpage),
                    DropdownMenuButton('API Reference', on_click=openUrsinaCheatSheetWebpage),
                )),
            )),
            DropdownMenu('Settings', buttons=(
                DropdownMenuSeparator(),
                DropdownMenu('View Mode', buttons=self.view_modes),
                DropdownMenu('VSYNC', buttons=(
                    DropdownMenuButton('On', on_click=enableVsync),
                    DropdownMenuButton('Off', on_click=disableVsync),
                )),
                DropdownMenu('Fullscreen', buttons=(
                    DropdownMenuButton('On', on_click=enableFullscreen),
                    DropdownMenuButton('Off', on_click=disableFullscreen),
                )),
                DropdownMenu('Borderless', buttons=(
                    DropdownMenuButton('On', on_click=enableBorderless),
                    DropdownMenuButton('Off', on_click=disableBorderless)
                ))
            ))
        ))

        self.menus = [self.model_menu, self.texture_menu, self.rename_window, self.top_menu]


    def load(self, name, folder=application.asset_folder / 'scenes'):
        for e in self.entities:
            destroy(e)
        self.entities.clear()
        scene_instance = None

        with open(f'test.py') as f:
            try:
                exec(f.read())
                scene_instance = eval(f'Scene()')
                self.entities = [e for e in scene.entities if e.has_ancestor(scene_instance)]
            except:
                print('error in scene:', name)

        # make icons
        for e in self.entities:
            e.editor_icon = EditorIcon(parent=self.editor_icon_parent, scene_editor=self, entity=e)
            self.editor_icons.append(e.editor_icon)
            e.collision = False

        if scene_instance:
            return scene_instance
        else:
            return False

    def set_attr_for_selected(self, name, value):
        # print('set:', name, value)
        for icon in self.selection:
            setattr(icon.entity, name, value)

        for menu in self.menus:
            menu.enabled = True if type(menu) == DropdownMenu else False

    def rename_selected(self, name=''):
        if not name:
            name = self.rename_window.content[0].text
        for icon in self.selection:
            icon.text = name
            icon.entity.name = name
            icon.text_entity.scale = 1

        self.rename_window.close()

    @property
    def show_names(self):
        return self._show_names

    @show_names.setter
    def show_names(self, value):
        self._show_names = value
        for icon in self.editor_icons:
            icon.text_entity.enabled = value

    def add_entity(self, name):
        e = Entity(name=name, model='cube')
        e.editor_icon = EditorIcon(parent=self.editor_icon_parent, scene_editor=self, entity=e)
        e.editor_icon.text_entity.text = name
        self.editor_icons.append(e.editor_icon)
        return e

    def delete_entity(self, selection):
        print('pass0')
        # self.editor_icons.remove(selection.editor_icon)
        print('pass1')
        destroy(selection.editor_icon)
        print('pass2')
        destroy(selection)
        print('pass3')

    def average_position_of_selection(self):
        _pos = Vec3(0, 0, 0)
        for icon in self.selection:
            _pos += icon.world_position
        _pos /= len(self.selection)
        return _pos

    def update(self):
        # print(b.name for i, b in scene.entities)
        for icon in self.editor_icons:
            icon.position = icon.entity.world_position
            icon.text_entity.look_at(camera, 'back')

        if self.rename_window.enabled:
            return

        if held_keys['control']:
            return

        if held_keys['x']:
            self.xPositionInput(selection=self.selection)
        if held_keys['y']:
            self.yPositionInput(selection=self.selection)
        if held_keys['z']:
            self.zPositionInput(selection=self.selection)

        if held_keys['s'] or held_keys['c']:
            self.singleScale()

        if held_keys['e']:
            self.multipleScale()

        # top_menu[1[3]].text = str(textures_buttons_list)
        # top_menu[1[5]].text = str(models_buttons_list)
        # top_menu[1[6]].text = str(models_buttons_list)

    def input(self, key):
        if key == 'escape':
            self.rename_window.enabled = False

        if key == 'enter':
            if self.rename_window.enabled:
                self.rename_window.content[1].on_click()

        if self.rename_window.enabled:
            return

        if key == 'shift' or key == 'alt':
            for e in self.editor_icons:
                e.ignore = True

        if key == 'shift up' or key == 'alt up':
            for e in self.editor_icons:
                e.ignore = False

        if key in ('x', 'y', 'z', 's', 'e', 'c') and self.selection and not held_keys['shift']:
            self.cursor_3d.visible = True
            self.cursor_3d.position = self.selection[-1].world_position

            if key == 'c':
                self.cursor_3d.position = self.average_position_of_selection()

            for icon in self.selection:
                icon.entity.original_parent = icon.entity.parent
                icon.entity.world_parent = self.cursor_3d

            if key == 'x' and key not in ('y', 'z'):
                self.cursor_3d.rulers[('x', 'y', 'z').index(key)].enabled = True
            elif key == 'y' and not key in ('x', 'z'):
                self.cursor_3d.rulers[('x', 'y', 'z').index(key)].enabled = True
            elif key == 'z' and not key in ('x', 'y'):
                self.cursor_3d.rulers[('x', 'y', 'z').index(key)].enabled = True

        if key in ('x up', 'y up', 'z up', 's up', 'e up', 'c up'):
            for icon in self.selection:
                # if hasattr(icon, 'original_parent'):
                icon.entity.world_parent = icon.entity.original_parent

            self.cursor_3d.visible = False
            for ruler in self.cursor_3d.rulers:
                ruler.enabled = False

        if key == 'm':
            if self.model_menu.enabled:
                self.model_menu.enabled = False
                self.editor_camera.ignore = True
            elif self.selection:
                self.model_menu.enabled = True

        if key == 't' and not held_keys['shift']:
            if self.texture_menu.enabled:
                self.texture_menu.enabled = False
            elif self.selection:
                self.texture_menu.enabled = True
                self.editor_camera.ignore = True

        if held_keys['shift'] and key == 't':
            self.show_names = not self.show_names

        if key == 'h':
            self.editor_icon_parent.enabled = not self.editor_icon_parent.enabled

        if key == 'l':
            from ursina.shaders import basic_lighting_shader
            for icon in self.editor_icons:
                # if not icon.entity.shader or not icon.entity.shader == basic_lighting_shader:
                icon.entity.shader = basic_lighting_shader
            # else:
            #     icon.entity.shader = None

        if key == 'n':
            e = self.add_entity('entity')
            e.position = self.average_position_of_selection()

        if held_keys['control'] and key == 'g':
            group = self.add_entity('group')
            for icon in self.selection:
                icon.entity.world_parent = group

        if key == 'f2' and self.selection:
            self.rename_window.enabled = True
            self.rename_window.content[0].active = True
            self.rename_window.content[0].text = ''

        if key == '1':
            self.editor_camera.rotation = (0, 0, 0)
        if key == '7':
            self.editor_camera.rotation = (90, 0, 0)
        if key == '5':
            camera.orthographic = not camera.orthographic

        if key == 'left mouse down':
            if self.duplicate_dragger.enabled:
                return

            for key in ('x', 'y', 'z', 's', 'e', 'c'):
                if held_keys[key]:
                    return

            icon = mouse.hovered_entity
            if held_keys['shift'] + held_keys['alt'] == 0:

                menu_is_open = True in [e.enabled for e in self.menus]
                if not menu_is_open:
                    if not icon in self.selection:
                        self.clear_selection()
                    # elif self.selection and icon != self.selection[-1]:
                    #     self.clear_selection()

            if not icon in self.editor_icons:
                return

            if not icon in self.selection:
                self.selection.append(icon)
            else:  # swap order
                print('swap')
                self.selection[-1], self.selection[self.selection.index(icon)] = self.selection[
                                                                                     self.selection.index(icon)], \
                                                                                 self.selection[-1]

            if held_keys['alt'] and icon in self.editor_icons:
                # print('deselect')
                self.selection.remove(icon)

            self.render_selection()

        if held_keys['shift'] and key == 'd' and self.selection:
            self.duplicate()

        if key == 'delete':
            for icon in self.selection:
                # print('delete:', icon.entity.name)
                self.delete_entity(icon.entity)
            self.clear_selection()

        if held_keys['control'] and key == 'z':
            self.undo()
        if held_keys['control'] and key == 'y':
            self.redo()

    def clear_selection(self):
        # print('clear selection')
        self.selection.clear()
        self.render_selection()
        self.model_menu.enabled = False

    def render_selection(self):
        for icon in self.editor_icons:
            icon.dot.color = color.white

        if self.selection:
            for icon in self.selection:
                icon.dot.color = color.azure

            self.selection[-1].dot.color = color.cyan

        self.selection_text.text = 'Selection:\n' + '\n'.join([icon.entity.name for icon in self.selection])

    def undo(self):
        pass

    def redo(self):
        pass

    def duplicate(self):
        try:
            self.duplicate_dragger.position = self.selection[-1].world_position

            for icon in self.selection:
                e = icon.entity
                clone = self.add_entity(name=icon.entity.name)
                clone.original_parent = e.parent
                clone.world_position = e.world_position
                clone.world_scale = e.world_scale
                clone.world_rotation = e.world_rotation
                clone.model = copy(e.model)
                clone.texture = e.texture
                clone.color = e.color
                clone.world_parent = self.duplicate_dragger

            self.clear_selection()
            self.selection = [e.editor_icon for e in self.duplicate_dragger.children]
            self.render_selection()
            self.duplicate_dragger.enabled = True
            self.duplicate_dragger.start_dragging()
        except error as err:
            print('Unable to duplicate selection\nError : ' + err)

    def xPositionInput(self, selection):
        value = TextField()
        for i in selection:
            i.x = value.text

    def yPositionInput(self, selection):
        value = TextField()
        for i in selection:
            i.y = value.text

    def zPositionInput(self, selection):
        value = TextField()
        for i in selection:
                i.z = value.text

    def destroySelection(self):
        try:
            self.delete_entity(selection=self.selection)
        except error as err:
            print('Unable to destroy Entity\nError : ' + err)

    def loadStuff(self):
        print(self.textures)
        print(self.models)
        self.textures_buttons = [DropdownMenuButton(text=str(i), on_click=Func(self.set_attr_for_selected, 'texture', i)) for i in self.textures]
        self.models_buttons = [DropdownMenuButton(text=str(i), on_click=Func(self.set_attr_for_selected, 'model', i)) for i in self.models]
        self.view_modes = [DropdownMenuButton(text=str(i)) for i in window.render_modes]

        self.shaders_fb = FileBrowser(file_types=['*.shader']).enabled = False # TO SET
        self.animations_fb = FileBrowser(file_types=['*.blend']).enabled = False # TO SET

        # self.separation = '-------------------------'

    def newEntity(self):
        e = self.add_entity('entity')
        e.position = self.average_position_of_selection()

    def saveData(self):
        selection = self.selection

    def getData(self):
        try:
            return selection
        except:
            print('error : no data saved')

    def changeTexture(self, texture):
        Func(self.set_attr_for_selected, 'texture', texture)


def openUrsinaForDummiesWebpage():
    wb.open('https://www.ursinaengine.org/entity_basics.html')

def openUrsinaCheatSheetWebpage():
    wb.open('https://www.ursinaengine.org/cheat_sheet.html')

def enableVsync():
    window.vsync = True # VSYNC can't be set while the window is open

def disableVsync():
    window.vsync = False # VSYNC can't be set while the window is open

def enableFullscreen():
    window.fullscreen = True

def disableFullscreen():
    window.fullscreen = False

def enableBorderless():
    window.borderless = True

def disableBorderless():
    window.borderless = False


if __name__ == '__main__':
    app = Ursina()
    scene_editor = SceneEditor()
    # Sky()

    app.run()
