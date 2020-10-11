from ursina import *

def update():
    global text_input
    if text_input.text == 'def':
        text_input.text = '<red>def<red>'


if __name__ == '__main__':
    ide = Ursina()

    text_input = TextField()
    text_input.text_entity.color = color.black

    window.color = color.white

    ide.run()