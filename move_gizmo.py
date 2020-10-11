from ursina import *
from round_arrow import RoundArrow

class MoveGizmo(Entity):
    def __init__(self):
        self.y_axis = Entity()