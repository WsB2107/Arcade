import time as time_module


class Timer:
    def __init__(self, auto_start: bool = False):
        self.is_running = False
        self.is_paused = False
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.pause_start_time = 0.0

        if auto_start:
            self.start()

    def start(self):

        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_time = time_module.time()
            self.elapsed_time = 0.0

    def pause(self):

        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time_module.time()
            self.elapsed_time = self.pause_start_time - self.start_time

    def resume(self):

        if self.is_running and self.is_paused:
            self.is_paused = False
            pause_duration = time_module.time() - self.pause_start_time
            self.start_time += pause_duration

    def stop(self):

        if self.is_running:
            self.is_running = False
            if not self.is_paused:
                self.elapsed_time = time_module.time() - self.start_time
        return self.elapsed_time

    def get_elapsed_time(self):

        if not self.is_running or self.is_paused:
            return self.elapsed_time
        return time_module.time() - self.start_time

    def get_formatted_time(self, show_milliseconds: bool = False):

        elapsed = self.get_elapsed_time()
        elapsed = max(0.0, elapsed)

        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60

        if show_milliseconds:
            milliseconds = int((elapsed - int(elapsed)) * 1000)
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        return f"{minutes:02d}:{seconds:02d}"

    def reset(self):

        was_running = self.is_running
        self.stop()
        self.elapsed_time = 0.0
        if was_running:
            self.start()
