####### SHINY APP #######
from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.input_text("name", "What's your name?", value="World"),
    ui.output_text("greeting"),
)


def server(input, output, session):
    @render.text
    def greeting():
        return f"Hello, {input.name()}!"


app = App(app_ui, server)
###################################


####### SHINY EXPRESS APP #######
from shiny.express import input, render, ui

ui.input_text("name", "What's your name?", value="World")


@render.text
def greeting():
    return f"Hello, {input.name()}!"


###################################
