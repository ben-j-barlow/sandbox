# https://shiny.posit.co/py/docs/nonblocking.html#:~:text=Shiny%20has%20async%20support%20as,parts%20of%20your%20Shiny%20app.

import asyncio
import concurrent.futures
import time

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("x", "x", value=1),
    ui.input_numeric("y", "y", value=2),
    ui.input_task_button("btn", "Add numbers"),
    ui.output_text("sum"),
)

# Execute the extended task logic on a different thread. To use a different
# process instead, use concurrent.futures.ProcessPoolExecutor.
pool = concurrent.futures.ThreadPoolExecutor()


def slow_sum(x, y):
    time.sleep(5)  # Simulate a slow synchronous task
    return x + y


def server(input, output, session):
    out = reactive.Value("Hello")

    @ui.bind_task_button(button_id="btn")
    @reactive.extended_task
    async def sum_values(x, y):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(pool, slow_sum, x, y)

    @reactive.effect
    @reactive.event(input.btn)
    def btn_click():
        sum_values(input.x(), input.y())

    @render.text
    def sum():
        return str(sum_values.result())


app = App(app_ui, server)
app.on_shutdown(pool.shutdown)
