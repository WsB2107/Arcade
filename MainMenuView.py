from levels import *
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIFlatButton
from LeaderboardView import Leaderboard
from SettingsView import Settings
from levels import Mines


class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.user = None
        self.ui_manager = UIManager()
        self.background_texture = arcade.load_texture('textures/main_menu.png')

        self.start_button = None
        self.leaderboard_button = None
        self.settings_button = None
        self.exit_button = None
        self.login_button = None

        self.create_ui()

    def create_ui(self):  # пользовательский интерфейс главного меню

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=20)

        title = UILabel(text="DUNGEON CRUSHERS", font_size=50, font_name="Arial", text_color=arcade.color.GOLD,
                        bold=True, align="center", width=600, height=60)
        vbox.add(title)

        if self.user and self.user.is_logged_in:
            user_label = UILabel(text=f"Игрок: {self.user.username} | ID: {self.user.user_id}", font_size=24,
                                 text_color=arcade.color.WHITE, align="center", width=400, height=30)
            vbox.add(user_label)

        else:
            self.login_button = UIFlatButton(text="ВОЙТИ / РЕГИСТРАЦИЯ", width=300, height=50)
            vbox.add(self.login_button)

        self.start_button = UIFlatButton(text="НАЧАТЬ ИГРУ", width=300, height=50)
        vbox.add(self.start_button)

        self.leaderboard_button = UIFlatButton(text="ТАБЛИЦА РЕКОРДОВ", width=300, height=50)
        vbox.add(self.leaderboard_button)

        self.settings_button = UIFlatButton(text="НАСТРОЙКИ", width=300, height=50)
        vbox.add(self.settings_button)

        self.exit_button = UIFlatButton(text="ВЫЙТИ", width=300, height=50)
        vbox.add(self.exit_button)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def on_show(self):  # показ меню

        self.ui_manager.enable()

    def on_hide(self):  # скрытие меню

        self.ui_manager.disable()

    def on_draw(self):  # отрисовка кадра

        self.clear()

        arcade.draw_texture_rect(self.background_texture, arcade.rect.XYWH(self.window.width // 2,
                                                                           self.window.height // 2,
                                                                           self.window.width,
                                                                           self.window.height))

        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):  # обработчик нажатия кнопки мыши

        self.ui_manager.on_mouse_press(x, y, button, modifiers)

        if self.start_button and self.start_button.rect:
            rect = self.start_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                game_view = Mines()
                game_view.main_menu = self
                self.window.show_view(game_view)
                return

        if self.leaderboard_button and self.leaderboard_button.rect:
            rect = self.leaderboard_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                leaderboard_view = Leaderboard(user=self.user, back_view=self)
                self.window.show_view(leaderboard_view)
                return

        if self.settings_button and self.settings_button.rect:
            rect = self.settings_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                settings_view = Settings(back_view=self)
                self.window.show_view(settings_view)
                return

        if self.exit_button and self.exit_button.rect:
            rect = self.exit_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                self.window.close()
                return

        if self.login_button and self.login_button.rect:
            rect = self.login_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                from LoginView import Login
                login_view = Login()
                self.window.show_view(login_view)
                return

    def on_mouse_motion(self, x, y, dx, dy):  # обработчик движения мыши

        self.ui_manager.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, key, modifiers):  # обработчик нажатия клавиш

        if key == arcade.key.ESCAPE:
            self.window.close()
