from config import *
from levels import *
from classes import *
import arcade
class Main(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        main_menu = MainMenuView()
        self.show_view(main_menu)


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture('textures/main_menu.png')

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(self.window.width // 2,
                                                  self.window.height // 2,
                                                  self.window.width,
                                                  self.window.height))
        arcade.draw_text("нажмите на пробел",
                         self.window.width / 2,
                         self.window.height / 2,
                         arcade.color.WHITE, 30,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = TestView()
            self.window.show_view(game_view)
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        if key == arcade.key.ESCAPE:
            self.window.close()



def setup_game(w = SCREEN_WIDTH, h = SCREEN_HEIGHT, t =SCREEN_TITLE):
    game = Main(w, h, t)
    return game

def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
