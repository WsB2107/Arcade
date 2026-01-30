import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIFlatButton


class Pause(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.ui_manager = UIManager()

        self.create_ui()

    def create_ui(self):

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=20, size_hint=(None, None))

        title = UILabel(text="ПАУЗА", font_size=50, font_name="Arial", text_color=arcade.color.GOLD, bold=True,
                        align="center", width=400, height=60)
        vbox.add(title)

        vbox.add(UILabel(text="", width=300, height=20))

        self.resume_button = UIFlatButton(text="ПРОДОЛЖИТЬ (ESC)", width=280, height=50)
        vbox.add(self.resume_button)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def on_show(self):

        self.ui_manager.enable()

    def on_hide(self):

        self.ui_manager.disable()

    def on_draw(self):

        self.clear()
        self.game_view.on_draw()
        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):

        self.ui_manager.on_mouse_press(x, y, button, modifiers)

        if self.resume_button.rect:
            rect = self.resume_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                self.game_view.paused = False
                self.window.show_view(self.game_view)
                return

    def on_mouse_motion(self, x, y, dx, dy):

        self.ui_manager.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, key, modifiers):

        if key == arcade.key.ESCAPE:
            self.game_view.paused = False
            self.window.show_view(self.game_view)
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
