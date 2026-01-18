from config import *
from levels import *
from classes import *
import arcade
from LoginView import Login

class Main(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        login_view=Login()
        self.show_view(login_view)

def setup_game(w = SCREEN_WIDTH, h = SCREEN_HEIGHT, t =SCREEN_TITLE):
    game = Main(w, h, t)
    return game

def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
