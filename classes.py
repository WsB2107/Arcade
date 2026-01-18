from config import *
from levels import *
import arcade


class Player(arcade.Sprite):
    def __init__(self, x, y):


        super().__init__("textures/test.jpg", scale=0.5)

        # стартовая позиция
        self.center_x = x
        self.center_y = y



    # self.take_damage() self.animate()
