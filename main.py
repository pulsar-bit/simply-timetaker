import flet as ft
import asyncio

from typing_inspection.typing_objects import target


def main(page: ft.Page):
    page.title = "Мой таймер"

    seconds = 0
    running = False

    time_text = ft.Text("00:00", size=40)

    def update_time():
        time_text.value = f"{seconds // 60:02d}:{seconds % 60:02d}"

    async def timer_loop():
        nonlocal seconds
        while True:
            await asyncio.sleep(1)
            if running:
                seconds += 1
                update_time()
                page.update()

    def start(e):
        nonlocal running
        running = True

    def pause(e):
        nonlocal running
        running = False

    def reset(e):
        nonlocal running, seconds
        running = False
        seconds = 0
        update_time()
        page.update()

    page.add(
        time_text,
        ft.Row(
            [
                ft.Button("Старт", on_click=start),
                ft.Button("Пауза", on_click=pause),
                ft.Button("Сброс", on_click=reset),
            ]
        ),
    )

    page.run_task(timer_loop)


ft.run(main, view=ft.AppView.WEB_BROWSER)
