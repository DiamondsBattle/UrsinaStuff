from ursina import *


if __name__ == '__main__':
    app = Ursina()

    bar = Slider(min=1, max=100)

    app.run()