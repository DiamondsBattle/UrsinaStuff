from ursina import *

colors = [color.white, color.yellow, color.orange, color.red, color.pink, color.peach]
current_color = 0

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, data):
        self.items.append(data)

    def pop(self):
        return self.items.pop()


app = Ursina()

def input(key):
    global current_color
    if key == 'space':
        current_color += 1
        stack.push(data=cube.color)
        try:
            cube.color = colors[current_color]
        except:
            current_color = 0
            cube.color = colors[current_color]
    if key == 'z':
        try:
            cube.color = stack.pop()
            print(cube.color)
        except:
            pass


cube = Entity(model='cube', color=color.white)
stack = Stack()
stack.push(cube.color)

app.run()