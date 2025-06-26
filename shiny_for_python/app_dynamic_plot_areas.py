from shiny import reactive
from shiny.express import input, ui, module
from shinywidgets import render_plotly
import numpy as np
import plotly.express as px
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)

@reactive.calc
def df():
    x = np.r_[1 : (2 + 1)]
    y = np.r_[1 : (2 + 1)]
    return pd.DataFrame({"x": x, "y": y})

@module
def plot_area(input, output, session):
    mult = reactive.value(1)
    
    with ui.layout_columns(col_widths=[8, 4]):
        with ui.card(full_screen=True):

            @render_plotly
            def hist():
                import plotly.express as px

                df_ = df()
                p = px.line(x=df_["x"], y=df_["y"] * mult.get())
                p.layout.update(showlegend=False)
                return p

        with ui.card(full_screen=False):
            ui.input_slider(
                id=f"slider", min=1, max=2, value=1, step=1, label=f"Control XX"
            )

    @reactive.effect
    def increment():
        mult.set(input.slider.get())
 
plot_area("one")
ui.hr()
plot_area("two")
