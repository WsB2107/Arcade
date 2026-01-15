from config import *
import arcade
class Main(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.window_width = width
        self.window_height = height

        self.texture = arcade.load_texture('textures/main_menu.png')
        self.set_fullscreen(True)

    def on_draw(self):

        self.clear()

        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.width // 2,
                                                                self.height // 2,
                                                                self.width, self.height))
        arcade.draw_text("нажмите на пробел",
                         self.width / 2, self.height / 2,
                         arcade.color.WHITE, 30,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):

        # выход из полноэкранного режима
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

            # если выходим из полноэкранного режима, восстанавливаем размер
            if not self.fullscreen:
                self.set_size(self.window_width, self.window_height)

                # помещаем окно в центр
                screen_info = arcade.get_screens()[0]
                x = (screen_info.width - self.window_width) // 2
                y = (screen_info.height - self.window_height) // 2
                self.set_location(x, y)

        #if key == arcade.key.SPACE:
            #self.show_view(GameView())

        if key == arcade.key.ESCAPE:
            self.close()


def setup_game(w = SCREEN_WIDTH, h = SCREEN_HEIGHT, t =SCREEN_TITLE):
    game = Main(w, h, t)
    return game

def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
