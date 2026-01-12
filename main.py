from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
import arcade
class Game(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        self.set_fullscreen(True)
    def setup(self):

        pass

    def on_draw(self):

        self.clear()

    def on_update(self, delta_time):

        pass

def setup_game(w = SCREEN_WIDTH, h = SCREEN_HEIGHT, t =SCREEN_TITLE):
    game = Game(w, h, t)
    return game

def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
