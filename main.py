"""
Flappy Bird клон на Kivy.
Управление: тап по экрану (или пробел) — птичка подпрыгивает.
Цель: пролетать сквозь щели между трубами и не врезаться.
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from random import randint

# Размер окна для теста на компьютере (на телефоне игнорируется).
if platform not in ("android", "ios"):
    Window.size = (400, 700)

# --- Настройки игры ---
GRAVITY = -1200.0          # ускорение падения (px/s^2)
JUMP_VELOCITY = 480.0      # скорость прыжка (px/s)
PIPE_SPEED = 220.0         # скорость труб (px/s)
PIPE_GAP = 200.0           # размер щели
PIPE_WIDTH = 70.0
PIPE_SPACING = 260.0       # расстояние между трубами
BIRD_SIZE = 40.0


class FlappyGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bird_pos = [0, 0]
        self.bird_vel = 0.0
        self.pipes = []          # каждая труба: {"x": float, "gap_y": float, "scored": bool}
        self.score = 0
        self.state = "start"     # start | play | over
        self._started = False

        self.score_label = Label(text="", font_size="42sp", bold=True)
        self.add_widget(self.score_label)
        self.msg_label = Label(text="", font_size="22sp", halign="center")
        self.add_widget(self.msg_label)

        Window.bind(on_key_down=self._on_key)
        Clock.schedule_once(self._setup, 0)

    def _setup(self, *_):
        self.reset()
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def reset(self):
        self.bird_pos = [self.width * 0.25, self.height * 0.5]
        self.bird_vel = 0.0
        self.score = 0
        self.pipes = []
        x = self.width + 200
        for _ in range(3):
            self.pipes.append(self._make_pipe(x))
            x += PIPE_SPACING
        self.state = "start"

    def _make_pipe(self, x):
        margin = 120
        gap_y = randint(int(margin + PIPE_GAP / 2),
                        int(self.height - margin - PIPE_GAP / 2))
        return {"x": x, "gap_y": float(gap_y), "scored": False}

    def _on_key(self, _win, key, *_args):
        # 32 = пробел, 273 = стрелка вверх
        if key in (32, 273):
            self.flap()
            return True
        return False

    def on_touch_down(self, touch):
        self.flap()
        return True

    def flap(self):
        if self.state == "start":
            self.state = "play"
            self.bird_vel = JUMP_VELOCITY
        elif self.state == "play":
            self.bird_vel = JUMP_VELOCITY
        elif self.state == "over":
            self.reset()

    def update(self, dt):
        if self.state == "play":
            self.bird_vel += GRAVITY * dt
            self.bird_pos[1] += self.bird_vel * dt

            for p in self.pipes:
                p["x"] -= PIPE_SPEED * dt

            # убираем ушедшие трубы и добавляем новые
            if self.pipes and self.pipes[0]["x"] < -PIPE_WIDTH:
                self.pipes.pop(0)
                last_x = self.pipes[-1]["x"]
                self.pipes.append(self._make_pipe(last_x + PIPE_SPACING))

            # очки
            for p in self.pipes:
                if not p["scored"] and p["x"] + PIPE_WIDTH < self.bird_pos[0]:
                    p["scored"] = True
                    self.score += 1

            self._check_collision()

        self.draw()

    def _check_collision(self):
        bx, by = self.bird_pos
        r = BIRD_SIZE / 2
        # пол и потолок
        if by - r <= 0 or by + r >= self.height:
            self.game_over()
            return
        for p in self.pipes:
            if p["x"] < bx + r and p["x"] + PIPE_WIDTH > bx - r:
                gap_top = p["gap_y"] + PIPE_GAP / 2
                gap_bottom = p["gap_y"] - PIPE_GAP / 2
                if by + r > gap_top or by - r < gap_bottom:
                    self.game_over()
                    return

    def game_over(self):
        self.state = "over"

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            # фон (небо)
            Color(0.43, 0.79, 0.93)
            Rectangle(pos=(0, 0), size=(self.width, self.height))
            # трубы
            Color(0.20, 0.65, 0.25)
            for p in self.pipes:
                gap_top = p["gap_y"] + PIPE_GAP / 2
                gap_bottom = p["gap_y"] - PIPE_GAP / 2
                # верхняя
                Rectangle(pos=(p["x"], gap_top),
                          size=(PIPE_WIDTH, self.height - gap_top))
                # нижняя
                Rectangle(pos=(p["x"], 0), size=(PIPE_WIDTH, gap_bottom))
            # птичка
            Color(0.98, 0.80, 0.18)
            Ellipse(pos=(self.bird_pos[0] - BIRD_SIZE / 2,
                         self.bird_pos[1] - BIRD_SIZE / 2),
                    size=(BIRD_SIZE, BIRD_SIZE))

        # текст
        self.score_label.pos = (self.width / 2 - 50, self.height - 90)
        self.score_label.size = (100, 50)
        self.msg_label.pos = (self.width / 2 - 150, self.height / 2 - 120)
        self.msg_label.size = (300, 60)

        if self.state == "start":
            self.score_label.text = ""
            self.msg_label.text = "Тапни, чтобы начать"
        elif self.state == "play":
            self.score_label.text = str(self.score)
            self.msg_label.text = ""
        else:
            self.score_label.text = ""
            self.msg_label.text = "Игра окончена!\nСчёт: %d — тапни для рестарта" % self.score

    def on_size(self, *_):
        # при первом получении размера расставляем объекты
        if not self._started and self.width > 1 and self.height > 1:
            self._started = True
            self.reset()


class FlappyApp(App):
    def build(self):
        return FlappyGame()


if __name__ == "__main__":
    FlappyApp().run()
