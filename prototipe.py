import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import flet as ft


REPORT_FILE = Path("timer_report.txt")
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"


class BaseEntity(ABC):


    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.get_name()!r})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.get_name() == other.get_name()

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.get_name() < other.get_name()

    def __hash__(self):
        return hash((self.__class__.__name__, self.get_name()))


class UserSession(BaseEntity):

    def __init__(self, login):
        self.login = login
        self.time_in = datetime.now()
        self.time_out = None

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        value = str(value).strip()
        self._login = value or "UserName"

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        if not isinstance(value, datetime):
            raise TypeError("time_in должен быть объектом datetime")
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        if value is not None and not isinstance(value, datetime):
            raise TypeError("time_out должен быть datetime или None")
        self._time_out = value

    def get_name(self):
        return self.login

    def __str__(self):
        return f"{self.login}: вход {self.time_in.strftime(TIME_FORMAT)}"

    def __repr__(self):
        return (
            f"UserSession(login={self.login!r}, "
            f"time_in={self.time_in!r}, time_out={self.time_out!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, UserSession):
            return NotImplemented
        return (self.login, self.time_in, self.time_out) == (
            other.login, other.time_in, other.time_out
        )

    def __lt__(self, other):
        if not isinstance(other, UserSession):
            return NotImplemented
        return self.time_in < other.time_in

    def __hash__(self):
        return hash((self.login, self.time_in, self.time_out))


class TimerPreset(BaseEntity):


    def __init__(self, title, seconds):
        self.title = title
        self.seconds = seconds

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Название пресета не может быть пустым")
        self._title = value

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Длительность должна быть целым числом >= 0")
        self._seconds = value

    def get_name(self):
        return self.title

    def __str__(self):
        return f"{self.title} ({self.seconds} сек.)"

    def __repr__(self):
        return f"TimerPreset(title={self.title!r}, seconds={self.seconds!r})"

    def __eq__(self, other):
        if not isinstance(other, TimerPreset):
            return NotImplemented
        return (self.title, self.seconds) == (other.title, other.seconds)

    def __lt__(self, other):
        if not isinstance(other, TimerPreset):
            return NotImplemented
        return self.seconds < other.seconds

    def __hash__(self):
        return hash((self.title, self.seconds))


class TimerController(BaseEntity):

    def __init__(self):
        self.seconds = 0
        self.running = False

    @property
    def elapsed_seconds(self):
        return self.seconds

    @elapsed_seconds.setter
    def elapsed_seconds(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Время должно быть целым числом >= 0")
        self.seconds = value

    @property
    def is_running(self):
        return self.running

    @is_running.setter
    def is_running(self, value):
        self.running = bool(value)

    def get_name(self):
        return "Таймер"

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False
        self.seconds = 0

    def tick(self):
        if self.running and self.seconds > 0:
            self.seconds -= 1
        elif self.seconds == 0:
            self.running = False

    @staticmethod
    def format_time(seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def __str__(self):
        return f"Таймер: {self.format_time(self.seconds)}"

    def __repr__(self):
        return f"TimerController(seconds={self.seconds!r}, running={self.running!r})"

    def __eq__(self, other):
        if not isinstance(other, TimerController):
            return NotImplemented
        return (self.seconds, self.running) == (other.seconds, other.running)

    def __lt__(self, other):
        if not isinstance(other, TimerController):
            return NotImplemented
        return self.seconds < other.seconds

    def __hash__(self):
        return hash((self.seconds, self.running))


class CustomMap(BaseEntity):

    def __init__(self):
        self._items = []

    @property
    def items(self):
        return tuple(self._items)

    def set(self, key, value):
        for index, (existing_key, _) in enumerate(self._items):
            if existing_key == key:
                self._items[index] = (key, value)
                return
        self._items.append((key, value))

    def get(self, key, default=None):
        for existing_key, value in self._items:
            if existing_key == key:
                return value
        return default

    def get_name(self):
        return "Пользовательская карта"

    def __str__(self):
        return f"CustomMap({len(self._items)} элементов)"

    def __repr__(self):
        return f"CustomMap(items={self._items!r})"

    def __eq__(self, other):
        if not isinstance(other, CustomMap):
            return NotImplemented
        return self._items == other._items

    def __lt__(self, other):
        if not isinstance(other, CustomMap):
            return NotImplemented
        return len(self._items) < len(other._items)

    def __hash__(self):
        return hash(tuple(self._items))


class TimerApplication(BaseEntity):

    def __init__(self, page: ft.Page):
        self.page = page
        self.timer = TimerController()
        self.session = None
        self.report_written = False
        self.presets = [
            TimerPreset("10 секунд", 10),
            TimerPreset("30 секунд", 30),
            TimerPreset("1 минута", 60),
            TimerPreset("2 минуты", 120),
            TimerPreset("5 минут", 300),
            TimerPreset("10 минут", 600),
            TimerPreset("15 минут", 900),
            TimerPreset("20 минут", 1200),
            TimerPreset("25 минут", 1500),
            TimerPreset("30 минут", 1800),
        ]
        self.metadata = CustomMap()
        self.metadata.set("application", "Мой таймер")
        self.metadata.set("report", str(REPORT_FILE))
        self._build_ui()

    def get_name(self):
        return "Приложение «Мой таймер»"

    def _build_ui(self):
        self.page.title = "Мой таймер"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 24
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.window_width = 520
        self.page.window_height = 680
        self.page.window_min_width = 360
        self.page.window_min_height = 520

        #заголовок
        self.heading = ft.Text(
            "Таймер", size=28, weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        #поле логина
        self.login_field = ft.TextField(
            label="Ваш логин", hint_text="Например, Адольф",
            prefix_icon=ft.Icons.PERSON, width=320, autofocus=True
        )
        #отображение времени
        self.time_text = ft.Text(
            "00:00", size=54, weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        #статус
        self.status_text = ft.Text(
            "Введите логин и нажмите «Старт»",
            size=14, text_align=ft.TextAlign.CENTER
        )
        #кнопка старта
        self.start_button = ft.Button(
            "Старт", icon=ft.Icons.PLAY_ARROW, on_click=self.start
        )
        # кнопка паузы
        self.pause_button = ft.Button(
            "Пауза", icon=ft.Icons.PAUSE, on_click=self.pause
        )
        #кнопка сброса
        self.reset_button = ft.Button(
            "Сброс", icon=ft.Icons.RESTART_ALT, on_click=self.reset
        )
        #выбор пресета
        self.preset_dropdown = ft.Dropdown(
            label="Быстрый выбор длительности",
            width=320,
            options=[
                ft.dropdown.Option(key=str(p.seconds), text=p.title)
                for p in self.presets
            ],
            on_select=self.choose_preset,
        )
        #индикатор прогресса
        self.progress = ft.ProgressBar(value=0, width=320)
        #разделитель
        self.divider = ft.Divider(height=1, thickness=1)
        # контейнеры и строки для выравнивания
        self.button_row = ft.Row(
            [self.start_button, self.pause_button, self.reset_button],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            wrap=True,
        )
        self.timer_card = ft.Container(
            content=ft.Column(
                [
                    self.time_text,
                    self.progress,
                    self.status_text,
                    self.button_row,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=24,
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.BLUE_GREY_200),
            width=380,
        )
        self.main_column = ft.Column(
            [
                self.heading,
                self.login_field,
                self.preset_dropdown,
                self.divider,
                self.timer_card,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.add(
            ft.Container(
                content=self.main_column,
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        )

    def start(self, event=None):
        if self.session is None:
            login = self.login_field.value or "UserName"
            self.session = UserSession(login)
        self.timer.start()
        self.status_text.value = f"Таймер запущен · пользователь: {self.session.login}"
        self.page.update()

    def pause(self, event=None):
        self.timer.pause()
        self.status_text.value = "Таймер на паузе"
        self.page.update()

    def reset(self, event=None):
        self.timer.reset()
        self.time_text.value = "00:00"
        self.progress.value = 0
        self.status_text.value = "Таймер сброшен"
        self.page.update()

    def choose_preset(self, event):
        selected = self.preset_dropdown.value

        if selected is not None:
            self.timer.pause()
            self.timer.elapsed_seconds = int(selected)

            self.time_text.value = self.timer.format_time(
                self.timer.elapsed_seconds
            )

            self.status_text.value = "Установлена выбранная длительность"
            self.progress.value = 0
            self.page.update()

    async def timer_loop(self):
        while True:
            await asyncio.sleep(1)
            self.timer.tick()
            if self.timer.is_running:
                self.time_text.value = self.timer.format_time(self.timer.elapsed_seconds)
                # Индикатор циклический, поскольку секундомер не имеет конечной цели.
                self.progress.value = (self.timer.elapsed_seconds % 60) / 60
                self.page.update()

    def save_report(self, event=None):
        if self.report_written:
            return
        self.report_written = True
        if self.session is None:
            self.session = UserSession(self.login_field.value or "UserName")
        self.session.time_out = datetime.now()

        header = (
            "+----------------+---------------------+---------------------+\n"
            "| login          | time_in             | time_out            |\n"
            "+----------------+---------------------+---------------------+\n"
        )
        row = (
            f"| {self.session.login[:14]:<14} | "
            f"{self.session.time_in.strftime(TIME_FORMAT):<19} | "
            f"{self.session.time_out.strftime(TIME_FORMAT):<19} |\n"
        )
        footer = "+----------------+---------------------+---------------------+\n"
        try:
            with REPORT_FILE.open("a", encoding="utf-8") as report:
                if REPORT_FILE.stat().st_size == 0:
                    report.write(header)
                report.write(row)
                report.write(footer)
        except OSError as error:
            print(f"Не удалось сохранить отчет: {error}")

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return f"TimerApplication(page={self.page!r})"

    def __eq__(self, other):
        if not isinstance(other, TimerApplication):
            return NotImplemented
        return self.get_name() == other.get_name()

    def __lt__(self, other):
        if not isinstance(other, TimerApplication):
            return NotImplemented
        return self.get_name() < other.get_name()

    def __hash__(self):
        return hash(self.get_name())


def main(page: ft.Page):
    app = TimerApplication(page)
    page.run_task(app.timer_loop)
    page.on_disconnect = app.save_report
    if hasattr(page, "on_close"):
        page.on_close = app.save_report


ft.run(main, view=ft.AppView.WEB_BROWSER)
