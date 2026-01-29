import arcade
from config import *


class VictoryView(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.TRANSPARENT_BLACK)
        self.texture = arcade.load_texture('textures/VictoryView.jpg')


    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(self.window.width // 2,
                                                  self.window.height // 2,
                                                  self.window.width,
                                                  self.window.height))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        if key == arcade.key.ESCAPE:
            self.window.close()