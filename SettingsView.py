import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIFlatButton, UISlider
from arcade.uicolor import WHITE


class Settings(arcade.View):
    def __init__(self, back_view=None):
        super().__init__()
        self.back_view = back_view
        self.ui_manager = UIManager()
        self.background_texture = arcade.load_texture('textures/main_menu.png')

        self.volume = 0.5
        self.dragging_slider = False

        self.create_ui()

    def create_ui(self):#создание интерфейса

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=10)

        title = UILabel(text="НАСТРОЙКИ", font_size=35, text_color=arcade.color.GOLD,
                        bold=True, align="center", width=350, height=40)
        vbox.add(title)

        self.volume_label = UILabel(text=f"Громкость: {int(self.volume * 100)}%",
                                    font_size=20, text_color=arcade.color.WHITE,
                                    align="center", width=250, height=25)
        vbox.add(self.volume_label)

        self.volume_slider = UISlider(value=self.volume, min_value=0.0, max_value=1.0,
                                      width=250, height=35)
        vbox.add(self.volume_slider)

        vbox.add(UILabel(text="", width=250, height=10))

        vbox.add(UILabel(text="ИНСТРУКЦИЯ:", font_size=28, text_color=arcade.color.WHITE,
                         align="center", width=350, height=30))

        instructions = ["Управление:",
                        "A/D или ←/→ - Движение",
                        "W - Прыжок",
                        "SPACE - Атака",
                        "ESC - Назад",]


        for line in instructions:
            vbox.add(UILabel(text=line, font_size=20, text_color=WHITE,align="left", width=350, height=20))

        vbox.add(UILabel(text="", width=250, height=10))

        buttons_hbox = UIBoxLayout(horizontal=True, space_between=10)

        self.back_button = UIFlatButton(text="НАЗАД", width=130, height=40)
        buttons_hbox.add(self.back_button)

        self.apply_button = UIFlatButton(text="ПРИМЕНИТЬ", width=130, height=40)
        buttons_hbox.add(self.apply_button)

        vbox.add(buttons_hbox)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def on_show(self):#показ окна
        self.ui_manager.enable()

    def on_hide(self):#скрытие окна
        self.ui_manager.disable()

    def on_draw(self):#отрисовка
        self.clear()
        arcade.draw_texture_rect(self.background_texture,arcade.rect.XYWH(self.window.width // 2,
                                                                          self.window.height // 2,
                                                                          self.window.width,
                                                                          self.window.height))
        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):#обработка нажатия мыши
        self.ui_manager.on_mouse_press(x, y, button, modifiers)

        if self.back_button and self.back_button.rect:
            rect = self.back_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                if self.back_view:
                    self.window.show_view(self.back_view)
                return

        if self.apply_button and self.apply_button.rect:
            rect = self.apply_button.rect
            if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                self.volume = self.volume_slider.value
                return

    def on_mouse_release(self, x, y, button, modifiers):#обработка отпускания мыши
        self.ui_manager.on_mouse_release(x, y, button, modifiers)
        self.dragging_slider = False

    def on_mouse_motion(self, x, y, dx, dy):#обновляет ползунок
        self.ui_manager.on_mouse_motion(x, y, dx, dy)
        if self.volume != self.volume_slider.value:
            self.volume = self.volume_slider.value
            self.volume_label.text = f"Громкость: {int(self.volume * 100)}%"

    def on_key_press(self, key, modifiers):#обработка нажатия клавиш
        if key == arcade.key.ESCAPE:
            if self.back_view:
                self.window.show_view(self.back_view)