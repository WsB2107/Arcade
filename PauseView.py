import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIFlatButton


class Pause(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.ui_manager = UIManager(self.window)

        self.create_ui()

    def create_ui(self):

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=20, size_hint=(None, None))

        title = UILabel(text="ПАУЗА", font_size=50, font_name="Arial", text_color=arcade.color.GOLD, bold=True,
                        align="center", width=400, height=60)
        vbox.add(title)

        vbox.add(UILabel(text="", width=300, height=20))

        self.resume_button = UIFlatButton(text="ПРОДОЛЖИТЬ (ESC)", width=280, height=50)
        self.resume_button.on_click = self.resume_game
        vbox.add(self.resume_button)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def resume_game(self, event=None):

        self.game_view.paused = False
        if self.game_view.timer.is_paused:
            self.game_view.timer.resume()
        self.window.show_view(self.game_view)

    def on_show_view(self):
        self.ui_manager.enable()

        if not self.game_view.paused:
            self.game_view.paused = True

        if not self.game_view.timer.is_paused:
            self.game_view.timer.pause()

    def on_hide_view(self):

        self.ui_manager.disable()

    def on_draw(self):

        self.clear()
        self.game_view.on_draw()
        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):

        self.ui_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):

        self.ui_manager.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.resume_game()
            return True
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            return True
        return False
