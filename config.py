import tkinter as tk

root = tk.Tk()
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
SCREEN_TITLE = "Dungeon Crushers"
PLAYER_MOVE_SPEED = 7
PLAYER_LADDER_SPEED = 4
ENEMY_MOVE_SPEED = 3
GRAVITY = 0.8
JUMP_SPEED = 15
COYOTE_TIME = 0.08  # Сколько после схода с платформы можно ещё прыгнуть
JUMP_BUFFER = 0.12  # Если нажали прыжок чуть раньше приземления, мы его «запомним» (тоже лайфхак для улучшения качества жизни игрока)
MAX_JUMPS = 1  # С двойным прыжком всё лучше, но не сегодня
CAMERA_LERP = 0.12
VOLUME = {"volume": 0.5}
root.destroy()
