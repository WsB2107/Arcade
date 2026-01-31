import arcade
from arcade.gui import UIManager, UIBoxLayout, UILabel, UIFlatButton, UIAnchorLayout


class VictoryView(arcade.View):
    def __init__(self, level_number=1, completion_time=0.0, user=None):
        super().__init__()
        self.level_number = level_number
        self.completion_time = completion_time

        self.ui_manager = UIManager()
        self.background_texture = None
        self.create_ui()
        self.background_texture = arcade.load_texture("textures/VictoryView.jpg")
        self.user = user

    def create_ui(self):

        self.ui_manager.clear()

        minutes = int(self.completion_time // 60)
        seconds = int(self.completion_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        vbox = UIBoxLayout(vertical=True, space_between=15)

        if self.level_number == 4:
            vbox.add(UILabel(text="Спасибо за игру!", font_size=28,
                             text_color=arcade.color.WHITE, width=400, height=35, align="center"))

        else:
            vbox.add(UILabel(text=f"""Уровень {self.level_number} пройден""", font_size=28,
                             text_color=arcade.color.WHITE, width=400, height=35, align="center"))

        vbox.add(UILabel(text=f"Время: {time_str}", font_size=24, text_color=arcade.color.WHITE,
                         width=400, height=30, align="center"))

        vbox.add(UILabel(text="", width=400, height=30))

        menu_btn = UIFlatButton(text="В ГЛАВНОЕ МЕНЮ", width=280, height=50)
        menu_btn.on_click = self.on_menu
        vbox.add(menu_btn)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def on_show_view(self):

        self.ui_manager.enable()
        self.save_record()

    def on_hide_view(self):

        self.ui_manager.disable()

    def on_draw(self):

        self.clear()

        arcade.draw_texture_rect(self.background_texture, arcade.rect.XYWH(self.window.width // 2,
                                                                           self.window.height // 2,
                                                                           self.window.width,
                                                                           self.window.height))

        self.ui_manager.draw()

    def on_key_press(self, key, modifiers):

        if key == arcade.key.ESCAPE:
            from MainMenuView import MainMenu
            self.window.show_view(MainMenu())
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)

    def save_record(self):

        if self.user and self.user.is_logged_in:
            from db import Database
            db = Database()
            db.save_record(self.user.user_id, self.level_number, self.completion_time)
            db.save_level_progress(self.user.user_id, self.level_number, self.completion_time)
            db.unlock_next_level(self.user.user_id, self.level_number)
            db.close()

    def on_menu(self, event=None):
        from MainMenuView import MainMenu
        menu_view = MainMenu()
        self.window.show_view(menu_view)
