import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIFlatButton
from db import Database


class Leaderboard(arcade.View):

    def __init__(self, user=None, back_view=None):

        super().__init__()
        self.user = user
        self.back_view = back_view
        self.ui_manager = UIManager()
        self.db = Database()
        self.background_texture = arcade.load_texture('textures/main_menu.png')

        self.showing_level_selection = True
        self.selected_level = None

        self.level1_button = None
        self.level2_button = None
        self.level3_button = None
        self.level4_button = None
        self.back_button = None
        self.back_to_levels_button = None

        self.create_level_selection_ui()

    def create_level_selection_ui(self):

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=15)

        title = UILabel(text="ТАБЛИЦА РЕКОРДОВ", font_size=45, text_color=arcade.color.GOLD, bold=True,
                        align="center", width=500, height=60)
        vbox.add(title)

        vbox.add(UILabel(text="Выберите уровень:", font_size=26, text_color=arcade.color.WHITE, align="center",
                         width=450, height=35))

        vbox.add(UILabel(text="", width=300, height=15))

        self.level1_button = UIFlatButton(text="ШАХТЫ", width=320, height=70)
        vbox.add(self.level1_button)

        self.level2_button = UIFlatButton(text="КАТАКОМБЫ", width=320, height=70)
        vbox.add(self.level2_button)

        self.level3_button = UIFlatButton(text="ГЛУБИНЫ", width=320, height=70)
        vbox.add(self.level3_button)

        self.level4_button = UIFlatButton(text="???", width=320, height=70)
        vbox.add(self.level4_button)

        vbox.add(UILabel(text="", width=300, height=20))

        self.back_button = UIFlatButton(text="НАЗАД В МЕНЮ", width=250, height=50)
        vbox.add(self.back_button)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

        self.showing_level_selection = True

    def create_leaderboard_ui(self, level_num):

        self.ui_manager.clear()

        vbox = UIBoxLayout(vertical=True, space_between=6)

        level_names = {1: "ШАХТЫ", 2: "КАТАКОМБЫ", 3: "ГЛУБИНЫ", 4: "???"}
        level_name = level_names.get(level_num, f"УРОВЕНЬ {level_num}")

        title = UILabel(text=f"РЕКОРДЫ: {level_name}", font_size=38, text_color=arcade.color.GOLD, bold=True,
                        align="center", width=500, height=60)
        vbox.add(title)

        vbox.add(UILabel(text="Топ-10 всех игроков", font_size=24, text_color=arcade.color.LIGHT_BLUE, align="center",
                         width=450, height=25))

        vbox.add(UILabel(text="", width=300, height=5))

        records = self.get_real_records_for_level(level_num)

        self.display_records(vbox, records, level_num)

        vbox.add(UILabel(text="", width=300, height=20))

        buttons_hbox = UIBoxLayout(horizontal=True, space_between=15)

        self.back_to_levels_button = UIFlatButton(text="ВЫБРАТЬ ДРУГОЙ УРОВЕНЬ", width=250, height=45)
        buttons_hbox.add(self.back_to_levels_button)

        vbox.add(buttons_hbox)

        anchor = UIAnchorLayout()
        anchor.add(child=vbox, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

        self.showing_level_selection = False
        self.selected_level = level_num

    def get_real_records_for_level(self, level_num):

        records = []

        all_users = self.db.get_all_users()

        for user_id, username in all_users:
            db_record = self.db.get_user_record(user_id, level_num)
            if db_record:
                best_time = db_record[2]
                is_current_user = self.user and self.user.is_logged_in and user_id == self.user.user_id
                records.append({"user_id": user_id, "username": username, "time": best_time,
                                "is_current_user": is_current_user})

        records.sort(key=lambda x: x["time"])

        for i, record in enumerate(records):
            record["place"] = i + 1

        return records

    def display_records(self, vbox, records, level_num):

        columns = UILabel(text="ИГРОК  |  ВРЕМЯ", font_size=22, text_color=arcade.color.LIGHT_GRAY,
                          align="center", width=500, height=35)
        vbox.add(columns)

        vbox.add(UILabel(text="", font_size=16, width=500, height=10))

        real_records = sorted(records, key=lambda x: x["time"])[:10] if records else []

        for place in range(1, 11):
            if place <= len(real_records):
                record = real_records[place - 1]
                username = record.get("username", "Unknown")
                time_sec = record.get("time", 0)

                if time_sec < 60:
                    time_str = f"{time_sec:.2f} сек"
                else:
                    minutes = int(time_sec // 60)
                    secs = time_sec % 60
                    time_str = f"{minutes}:{secs:05.2f}"

                if place == 1:
                    color = arcade.color.GOLD
                elif place == 2:
                    color = arcade.color.SILVER
                elif place == 3:
                    color = arcade.color.BRONZE
                else:
                    color = arcade.color.WHITE

                display_name = username

                display_text = f"{place}.  {display_name}  {time_str}"

                record_text = UILabel(text=display_text, font_size=16, text_color=color,
                                      align="left", width=500, height=26)
            else:

                display_text = f"{place}"
                record_text = UILabel(text=display_text, font_size=14, text_color=arcade.color.DARK_GRAY,
                                      align="left", width=500, height=24)

            vbox.add(record_text)

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

        if self.showing_level_selection:
            if self.level1_button and self.level1_button.rect:
                rect = self.level1_button.rect
                if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                    self.create_leaderboard_ui(1)
                    return

            if self.level2_button and self.level2_button.rect:
                rect = self.level2_button.rect
                if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                    self.create_leaderboard_ui(2)
                    return

            if self.level3_button and self.level3_button.rect:
                rect = self.level3_button.rect
                if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                    self.create_leaderboard_ui(3)
                    return

            if self.level4_button and self.level4_button.rect:
                rect = self.level4_button.rect
                if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                    self.create_leaderboard_ui(4)
                    return

            if self.back_button and self.back_button.rect:
                rect = self.back_button.rect
                if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                    if self.back_view:
                        self.window.show_view(self.back_view)
                    return
        else:
            if self.back_to_levels_button and self.back_to_levels_button.rect:
                rect = self.back_to_levels_button.rect
                if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                    self.create_level_selection_ui()
                    return

    def on_key_press(self, key, modifiers):

        if key == arcade.key.ESCAPE:
            if self.showing_level_selection:
                if self.back_view:
                    self.window.show_view(self.back_view)
            else:
                self.create_level_selection_ui()

    def on_mouse_motion(self, x, y, dx, dy):

        self.ui_manager.on_mouse_motion(x, y, dx, dy)
