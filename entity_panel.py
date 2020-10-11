from ursina import *
import ursina

class Text(Entity):
    size = .025
    default_font = 'OpenSans-Regular.ttf'
    default_resolution = 1080 * size * 2
    start_tag = '<'
    end_tag = '>'

    def __init__(self, background_color=None, text='', start_tag=start_tag, end_tag=end_tag, ignore=True, **kwargs):
        super().__init__(ignore=ignore)
        self.size = Text.size
        self.parent = camera.ui

        self.setColorScaleOff()
        self.text_nodes = list()
        self.images = list()
        self.origin = (-.5, .5)

        self.font = Text.default_font
        self.resolution = Text.default_resolution
        self.line_height = 1
        self.use_tags = True
        self.start_tag = start_tag
        self.end_tag = end_tag
        self.text_colors = {'default': color.text_color}

        for color_name in color.color_names:
            self.text_colors[color_name] = color.colors[color_name]

        self.tag = Text.start_tag + 'default' + Text.end_tag
        self.current_color = self.text_colors['default']
        self.scale_override = 1
        self._background = None
        self._background_color = background_color
        self.appear_sequence = None  # gets created when calling appear()

        if text != '':
            self.text = text

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def text(self):
        t = ''
        y = 0
        if self.text_nodes:
            # y = self.text_nodes[0].getZ()
            y = self.text_nodes[0].getY()

        for tn in self.text_nodes:
            # if y != tn.getZ():
            if y != tn.getY():
                t += '\n'
                # y = tn.getZ()
                y = tn.getY()

            t += tn.node().text

        return t

    @text.setter
    def text(self, text):
        self.raw_text = text
        text = self.start_tag + self.end_tag + str(text)  # start with empty tag for alignemnt to work?

        self.images.clear()
        for tn in self.text_nodes:
            tn.remove_node()

        self.text_nodes.clear()

        if not self.start_tag in text or not self.end_tag in text or self.use_tags == False:
            self.create_text_section(text)
            return

        sections = list()
        section = ''
        tag = self.start_tag + 'default' + self.end_tag
        temp_text_node = TextNode('temp_text_node')
        temp_text_node.setFont(self.font)
        x = 0
        y = 0

        i = 0
        while i < len(text):
            char = text[i]
            if char == '\n':
                sections.append([section, tag, x, y])
                section = ''
                y -= 1
                x = 0
                i += 1

            elif char == self.start_tag:  # find tag
                sections.append([section, tag, x, y])
                x += temp_text_node.calcWidth(section)
                section = ''

                tag = ''
                for j in range(len(text) - i):
                    tag += text[i + j]
                    if text[i + j] == self.end_tag and len(tag) > 0:
                        i += j + 1
                        break
            else:
                section += char
                i += 1

        sections.append([section, tag, x, y])

        for i, s in enumerate(sections):
            tag = s[1]
            # move the text after image one space right
            if tag.startswith(self.start_tag + 'image:'):
                for f in sections:
                    if f[3] == s[3] and f[2] > s[2]:
                        f[2] += .5

                s[2] += .5

            self.create_text_section(text=s[0], tag=s[1], x=s[2], y=s[3])

        self.align()

    def update_text(self):
        self.text = self.raw_text

    def create_text_section(self, text, tag='', x=0, y=0):
        # print(text, tag)
        self.text_node = TextNode('t')
        self.text_node_path = self.attachNewNode(self.text_node)
        try:
            self.text_node.setFont(self._font)
        except:
            pass  # default font

        if tag != '<>':
            tag = tag[1:-1]

            if tag.startswith('hsb('):  # set color based on numbers
                tag = tag[4:-1]
                hsb_values = tuple(float(e.strip()) for e in tag.split(','))
                self.current_color = color.color(*hsb_values)

            elif tag.startswith('rgb('):  # set color based on numbers
                tag = tag[4:-1]
                rgb_values = (float(e.strip()) for e in tag.split(','))
                self.current_color = color.rgba(*rgb_values)

            if tag.startswith('scale:'):
                scale = tag.split(':')[1]
                self.scale_override = float(scale)

            elif tag.startswith('image:'):
                texture_name = tag.split(':')[1]
                image = Entity(
                    parent=self.text_node_path,
                    name='inline_image',
                    model='quad',
                    texture=texture_name,
                    color=self.current_color,
                    scale=1,
                    # position=(x*self.size*self.scale_override, y*self.size*self.line_height),
                    origin=(.0, -.25),
                    add_to_scene_entities=False,
                )
                if not image.texture:
                    destroy(image)
                else:
                    self.images.append(image)
                    # self.text_node.remove_node()
                    # self.text_node = image
            else:
                if tag in self.text_colors:
                    self.current_color = self.text_colors[tag]

        self.text_node_path.setScale(self.scale_override * self.size)
        self.text_node.setText(text)
        self.text_node.setTextColor(self.current_color)
        self.text_node.setPreserveTrailingWhitespace(True)
        # self.text_node_path.setPos(
        #     x * self.size * self.scale_override,
        #     0,
        #     (y * self.size * self.line_height) - .75 * self.size)
        self.text_node_path.setPos(
            x * self.size * self.scale_override,
            (y * self.size * self.line_height) - .75 * self.size,
            0)
        self.text_nodes.append(self.text_node_path)

        return self.text_node

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        font = loader.loadFont(value)
        if font:
            self._font = font
            self._font.clear()  # remove assertion warning
            self._font.setPixelsPerUnit(self.resolution)
            self.text = self.raw_text  # update tex

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.current_color = value
        self.text_colors['default'] = value
        for tn in self.text_nodes:
            tn.node().setTextColor(value)

    @property
    def line_height(self):
        try:
            return self._line_height
        except:
            return 1

    @line_height.setter
    def line_height(self, value):
        self._line_height = value
        self.text = self.raw_text

    @property
    def width(self):
        if not hasattr(self, 'text'):
            return 0

        temp_text_node = TextNode('temp')
        temp_text_node.setFont(self._font)

        longest_line_length = 0
        for line in self.text.split('\n'):
            longest_line_length = max(longest_line_length, temp_text_node.calcWidth(line))

        return longest_line_length * self.scale_x * self.size

    @property
    def height(self):
        return (len(self.lines) * self.line_height * self.scale_y * self.size)

    @property
    def lines(self):
        return self.text.splitlines()

    @property
    def resolution(self):
        return self._font.getPixelsPerUnit()

    @resolution.setter
    def resolution(self, value):
        self._font.setPixelsPerUnit(value)

    @property
    def wordwrap(self):
        if hasattr(self, '_wordwrap'):
            return self._wordwrap
        else:
            return 0

    @wordwrap.setter
    def wordwrap(self, value):
        self._wordwrap = value
        new_text = ''
        is_in_tag = False
        i = 0
        for word in self.raw_text.replace('\n', ' ').replace(self.end_tag, self.end_tag + ' ').split(' '):

            if word.startswith(self.start_tag) and new_text:
                new_text = new_text[:-1]

            if not word.startswith(self.start_tag):
                i += len(word)

            if i >= value:
                new_text += '\n'
                i = 0

            new_text += word + ' '

        # print('--------------------\n', new_text)
        self.text = new_text

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value
        if self.text:
            self.text = self.raw_text

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self):
        if self.background_color is None:
            self.background_color = color.black66
        else:
            pass

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        print(self.background_color)
        if value == True:
            if self.background_color is not None:
                self.create_background(color=self.background_color)
            else:
                self.create_background()
        elif self._background:
            destroy(self._background)

    def align(self):
        value = self.origin
        linewidths = [self.text_nodes[0].node().calcWidth(line) for line in self.lines]
        # print('.........', linewidths)
        for tn in self.text_nodes:
            # center text horizontally
            # linenumber = abs(int(tn.getZ() / self.size / self.line_height))
            linenumber = abs(int(tn.getY() / self.size / self.line_height))
            tn.setX(tn.getX() - (linewidths[linenumber] / 2 * self.size * tn.getScale()[0] / self.size))
            # tn.setX(tn.getX() - (linewidths[linenumber] / 2 * self.size))
            # add offset based on origin/value
            # x -= half line width * text node scale
            tn.setX(
                tn.getX() - (linewidths[linenumber] / 2 * value[0] * 2 * self.size) * tn.getScale()[0] / self.size
            )
            # center text vertically
            halfheight = len(linewidths) * self.line_height / 2
            # tn.setZ(tn.getZ() + (halfheight * self.size))
            tn.setY(tn.getY() + (halfheight * self.size))
            # add offset
            # tn.setZ(tn.getZ() - (halfheight * value[1] * 2 * self.size))
            tn.setY(tn.getY() - (halfheight * value[1] * 2 * self.size))

    def create_background(self, padding=size * 2, radius=size, color=ursina.color.black66):
        from ursina import Quad, destroy

        if self._background:
            destroy(self._background)

        self._background = Entity(parent=self, z=.01)

        if isinstance(padding, (int, float, complex)):
            padding = (padding, padding)

        w, h = self.width + padding[0], self.height + padding[1]
        self._background.x -= self.origin_x * self.width
        self._background.y -= self.origin_y * self.height

        self._background.model = Quad(radius=radius, scale=(w / self.scale_x, h / self.scale_y))
        self._background.color = color

    def appear(self, speed=.025, delay=0):
        from ursina.ursinastuff import invoke
        self.enabled = True
        # self.visible = True   # setting visible seems to reset the colors
        if self.appear_sequence:
            self.appear_sequence.finish()

        x = 0
        self.appear_sequence = Sequence()
        for i, tn in enumerate(self.text_nodes):
            target_text = tn.node().getText()
            tn.node().setText('')
            new_text = ''

            for j, char in enumerate(target_text):
                new_text += char
                self.appear_sequence.append(Wait(speed))
                self.appear_sequence.append(Func(tn.node().setText, new_text))

        self.appear_sequence.start()
        return self.appear_sequence

    def get_width(string, font=None):
        t = Text(string)
        if font:
            t.font = font
        w = t.width
        from ursina import destroy
        destroy(t)
        return w


app = Ursina()

window.color = color.white

panel = Text(background=True,
             background_color=color.pink,
             text=f'Name : Weapon\n\
Model : gun_model (OBJ)\n\
Texture : camo_desert (PNG)\n\
Color : #8738H3 (RGB)\n\
Vertices : 735283\n\
Triangles : 2732\n\
Pos : 73; 736; 142 (Vec3)\n\
Collider : None\n\
Body : RigidBody')

app.run()
