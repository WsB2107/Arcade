import arcade
from arcade.gui import (UIManager, UIBoxLayout, UILabel, UIInputText, UIFlatButton, UIAnchorLayout)
from db import Database
from user import User
from MainMenuView import MainMenu


class Login(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.mode = "login"
        self.background_texture = arcade.load_texture("textures/main_menu.png")

        self.db = Database()
        self.user = User()

        self.action_button = None
        self.switch_button = None
        self.username_input = None
        self.password_input = None
        self.confirm_input = None
        self.create_ui()
        self.window.set_fullscreen()

    def create_ui(self):  # создание пользовательского интерфейса

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=10)

        if self.mode == "login":
            title = "ВХОД В ИГРУ"
        else:
            title = "РЕГИСТРАЦИЯ"
        vbox.add(UILabel(text=title, font_size=32, text_color=arcade.color.GOLD, bold=True, width=400, height=50,
                         align="center"))

        vbox.add(UILabel(text="", width=300, height=20))

        vbox.add(UILabel(text="Имя пользователя:", font_size=20, text_color=arcade.color.WHITE, width=300, height=25))
        self.username_input = UIInputText(text="", width=300, height=40, font_size=20)
        vbox.add(self.username_input)

        vbox.add(UILabel(text="", width=300, height=15))

        vbox.add(UILabel(text="Пароль:", font_size=20, text_color=arcade.color.WHITE, width=300, height=25))
        self.password_input = UIInputText(text="", width=300, height=40, font_size=20)
        vbox.add(self.password_input)

        if self.mode == "register":
            vbox.add(UILabel(text="", width=300, height=15))
            vbox.add(UILabel(text="Подтвердите пароль:", font_size=20, text_color=arcade.color.WHITE,
                             width=300, height=25))

            self.confirm_input = UIInputText(text="", width=300, height=40, font_size=20)
            vbox.add(self.confirm_input)

        vbox.add(UILabel(text="", width=300, height=30))

        if self.mode == "login":
            action_text = "ВОЙТИ"
        else:
            action_text = "ЗАРЕГИСТРИРОВАТЬСЯ"

        self.action_button = UIFlatButton(text=action_text, width=250, height=45)
        vbox.add(self.action_button)

        vbox.add(UILabel(text="", width=300, height=10))

        if self.mode == "login":
            switch_text = "Нет аккаунта? Регистрация"
        else:
            switch_text = "Есть аккаунт? Войти"

        self.switch_button = UIFlatButton(text=switch_text, width=250, height=35)
        vbox.add(self.switch_button)

        vbox.add(UILabel(text="", width=300, height=15))

        self.message_label = UILabel(text="", font_size=18, text_color=arcade.color.WHITE, width=400, height=30,
                                     align="center")
        vbox.add(self.message_label)

        anchor_layout = UIAnchorLayout()
        anchor_layout.add(child=vbox, anchor_x="center", anchor_y="center")

        self.ui_manager.add(anchor_layout)

    def on_action_button_click(self):  # обработчик нажатия кнопки вход или регистрация

        username = self.username_input.text
        password = self.password_input.text

        if self.mode == "login":
            success, message = self.user.login(username, password)
            if success:
                self.set_message(f"Вход выполнен! {message}", arcade.color.GREEN)
                arcade.schedule_once(self.go_to_main_menu, 1.0)
            else:
                self.set_message(f"Ошибка: {message}", arcade.color.RED)

        else:
            confirm = self.confirm_input.text
            if password != confirm:
                self.set_message("Пароли не совпадают!", arcade.color.RED)
                return

            success, message = self.user.register(username, password)

            if success:
                self.set_message(f"Регистрация успешна! {message}", arcade.color.GREEN)
                arcade.schedule_once(self.go_to_main_menu, 1.0)
            else:
                self.set_message(f"Ошибка: {message}", arcade.color.RED)

    def set_message(self, text, color):  # метод для отображения сообщений

        self.message_label.text = text
        self.message_label.text_color = color

    def on_show(self):  # вызывается при показе окна

        self.ui_manager.enable()

    def on_hide(self):  # вызывается при скрытии окна

        self.ui_manager.disable()

    def on_draw(self):  # метод отрисовки кадра

        self.clear()

        rect = arcade.rect.XYWH(self.window.width // 2, self.window.height // 2, self.window.width, self.window.height)
        arcade.draw_texture_rect(self.background_texture, rect)

        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):  # обработчик нажатия кнопки мыши

        if self.action_button:
            rect = self.action_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                self.on_action_button_click()
                return

        if self.switch_button:
            rect = self.switch_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                self.mode = "register" if self.mode == "login" else "login"
                self.create_ui()
                return

        self.ui_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):  # обработчик движения мыши

        self.ui_manager.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, key, modifiers):  # обработчик нажатия клавиш

        self.ui_manager.on_key_press(key, modifiers)

        if key == arcade.key.ENTER:
            self.on_action_button_click()
        elif key == arcade.key.ESCAPE:
            self.go_to_main_menu()
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)

    def on_text(self, text):  # обработчик ввода текста

        self.ui_manager.on_text(text)

    def on_text_motion(self, motion):  # для backspace

        self.ui_manager.on_text_motion(motion)

    def go_to_main_menu(self, delta_time=None):  # переход в главное меню

        menu = MainMenu()
        menu.user = self.user
        self.window.show_view(menu)
        self.db.close()
