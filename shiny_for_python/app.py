import matplotlib.pyplot as plt
import numpy as np
from shiny import ui, render, App, module, reactive
from shinywidgets import render_plotly, output_widget
from datetime import datetime
import pandas as pd
import plotly.express as px

PLOTS = 2

import re

def parse_parameterised_sql(sql) -> set[str]:
    parameter_universe_with_colon = set(re.findall(r':[a-zA-Z_][a-zA-Z-_]*(?=\s|,|\)|$)', sql))
    return {param[1:] for param in parameter_universe_with_colon}

df_columns = ["agg_metric_period", "agg_metric_value", "is_spike"]
df = pd.DataFrame(
    {
        "agg_metric_period": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "agg_metric_value": np.random.rand(10) * 100,
        "is_spike": [False, False, True, False, False, True, False, False, False, False],
    }
)

card_plot = ui.card(
    ui.card_header("Plot 1"),
    output_widget("plot_1"),
    full_screen=True,
)

card_input = ui.card(
    ui.card_header("Input"),
    ui.input_slider("slider_1", "Slider 1", value=3, min=1, max=5, step=1),
)

def make_items():
    return [
        ui.accordion_panel(
            f"Section {i}",                   
            ui.layout_columns(
                ui.card(
                    ui.card_header(f"Plot {i}"),
                    output_widget(f"plot_{i}"),
                    full_screen=True,
                ),
                ui.card(
                    ui.card_header("Input"),
                    ui.input_slider(f"slider_{i}", f"Slider {i}", value=3, min=1, max=i + 2, step=i),
                ),
                width="100%",
                col_widths=[9, 3],
            )
        )
        for i in range(1, PLOTS + 1)
    ]

app_ui = ui.page_fluid(
    ui.panel_title("Dynamic number of plots"),
    ui.card(
        ui.card_header("Enter parameterised SQL"),
        ui.layout_columns(
            ui.input_text_area("SQL_INPUT", label="SQL Input", value="SELECT * FROM table WHERE period = :period", rows=6, width="100%"),
            ui.output_text_verbatim("output_sql_parameters"),
            width="100%",
            col_widths=[8, 4],
        ),
    ),
    ui.input_action_button("submit_query", "Submit Query"),
    ui.accordion(*make_items(), id="acc", multiple=True),
)

def server(input, output, session):
    @render_plotly
    def plot_1():
        return px.scatter(
            df,
            x="agg_metric_period",
            y="agg_metric_value",
            color="is_spike",
            title=f"Plot 1: Slider value is {input.slider_1()}",
        )
    
    @render_plotly
    def plot_2():
        return px.scatter(
            df,
            x="agg_metric_period",
            y="agg_metric_value",
            color="is_spike",
            title=f"Plot 2: Slider value is {input.slider_2()}",
        )
    
    @reactive.effect
    @reactive.event(input.submit_query)
    def _handle_submit_query():
        parameterised_sql = input.SQL_INPUT()
        
    @render.text
    def output_sql_parameters():
        parameterised_sql = input.SQL_INPUT()
        parameter_universe = parse_parameterised_sql(parameterised_sql)
        return "\n".join(sorted(parameter_universe)) if parameter_universe else "No parameters found in SQL input."

app = App(app_ui, server)
