from levels import *
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIFlatButton
from db import Database

class LevelSelect(arcade.View):
    def __init__(self, main_menu=None, user=None):
        super().__init__()
        self.main_menu = main_menu
        self.user = user
        self.ui_manager = UIManager()

        self.background_texture = arcade.load_texture('textures/main_menu.png')
        self.db = Database()

        self.user_id = self.db.get_user_id(self.user.username) if self.user else None

        self.unlocked_levels = self.get_unlocked_levels()

        self.create_ui()

    def get_unlocked_levels(self):

        if self.user_id:
            unlocked = self.db.get_unlocked_levels(self.user_id)
            return unlocked if unlocked else [1]
        return [1]

    def is_level_unlocked(self, level_num):

        if self.user_id:
            return self.db.is_level_unlocked(self.user_id, level_num)
        return level_num == 1

    def create_ui(self):

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=20)

        title = UILabel(text="ВЫБОР УРОВНЯ", font_size=50, font_name="Arial", text_color=arcade.color.GOLD,
                        bold=True, align="center", width=800, height=60)
        vbox.add(title)

        levels_grid = UIBoxLayout(vertical=True, space_between=30)

        row1 = UIBoxLayout(vertical=False, space_between=40)

        level1_button = UIFlatButton(text="1. ШАХТЫ", width=300, height=80)
        self.level1_button = level1_button
        row1.add(level1_button)

        level2_enabled = self.is_level_unlocked(2)
        level2_text = "2. КАТАКОМБЫ"
        level2_button = UIFlatButton(text=level2_text, width=300, height=80)
        if not level2_enabled:
            level2_button.disabled = True
            level2_button.text_color = arcade.color.DARK_GRAY
        self.level2_button = level2_button
        row1.add(level2_button)

        levels_grid.add(row1)

        row2 = UIBoxLayout(vertical=False, space_between=40)

        level3_enabled = self.is_level_unlocked(3)
        level3_text = "3. ГЛУБИНЫ"
        level3_button = UIFlatButton(text=level3_text, width=300, height=80)
        if not level3_enabled:
            level3_button.disabled = True
            level3_button.text_color = arcade.color.DARK_GRAY
        self.level3_button = level3_button
        row2.add(level3_button)

        level4_enabled = self.is_level_unlocked(4)
        level4_text = "4. ???"
        level4_button = UIFlatButton(text=level4_text, width=300, height=80)
        if not level4_enabled:
            level4_button.disabled = True
            level4_button.text_color = arcade.color.DARK_GRAY
        self.level4_button = level4_button
        row2.add(level4_button)

        levels_grid.add(row2)

        vbox.add(levels_grid)

        self.back_button = UIFlatButton(text="НАЗАД В МЕНЮ", width=300, height=50)
        vbox.add(self.back_button)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def on_show(self):

        self.ui_manager.enable()

    def on_hide(self):

        self.ui_manager.disable()

    def on_draw(self):

        self.clear()

        arcade.draw_texture_rect(self.background_texture, arcade.rect.XYWH(self.window.width // 2,
                                                                           self.window.height // 2,
                                                                           self.window.width,
                                                                           self.window.height))

        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):

        self.ui_manager.on_mouse_press(x, y, button, modifiers)

        if self.level1_button.rect:
            rect = self.level1_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                self.start_level("mines")
                return

        if self.level2_button.rect:
            rect = self.level2_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                if not self.level2_button.disabled:
                    self.start_level("catacombs")
                return

        if self.level3_button.rect:
            rect = self.level3_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                if not self.level3_button.disabled:
                    self.start_level("???")
                return

        if self.level4_button.rect:
            rect = self.level4_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                if not self.level4_button.disabled:
                    self.start_level("???")
                return

        if self.back_button.rect:
            rect = self.back_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                if self.main_menu:
                    self.window.show_view(self.main_menu)
                return

    def on_mouse_motion(self, x, y, dx, dy):

        self.ui_manager.on_mouse_motion(x, y, dx, dy)

    def start_level(self, level_name):

        self.ui_manager.disable()

        level_num = 1
        if level_name == "mines":
            self.window.set_fullscreen()
            game_view = Mines()
            level_num = 1
        elif level_name == "catacombs":
            self.window.set_fullscreen()
            game_view = Catacombs()
            level_num = 2
        elif level_name == "???":
            self.window.set_fullscreen()
            level_num = 3
        elif level_name == "???":
            self.window.set_fullscreen()
            level_num = 4

        self.window.set_fullscreen(True)

        game_view.main_menu = self.main_menu
        game_view.user = self.user
        game_view.level_num = level_num

        self.window.show_view(game_view)

    def on_key_press(self, key, modifiers):

        if key == arcade.key.ESCAPE:
            if self.main_menu:
                self.window.show_view(self.main_menu)

        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
