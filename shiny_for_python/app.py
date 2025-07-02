import matplotlib.pyplot as plt
import numpy as np
from shiny import ui, render, App, module, reactive
from shinywidgets import render_plotly, output_widget, render_widget
from datetime import datetime
import pandas as pd
import plotly.express as px
import re

PLOTS = 1

def parse_parameterised_sql(sql) -> set[str]:
    matches = set(re.findall(r'\{(.*?)\}', sql))
    parameter_universe = {}

    for match in matches:
        parts = [p.strip() for p in match.split(',')]
        param_id = parts[0]
        kv_pairs = parts[1:]

        param_dict = {}
        for kv in kv_pairs:
            if '=' in kv:
                k = kv.split('=')[0].strip()
                v = kv.split('=')[1].strip()
                if k in ['min', 'max', 'step']:
                    v = float(v)
                param_dict[k] = v
            else:
                # For robustness — handle invalid key-value cases
                continue

        parameter_universe[param_id] = param_dict
    return parameter_universe

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
                    id=f"input_card_{i}",
                ),
                width="100%",
                col_widths=[8, 4],
            )
        )
        for i in range(1, PLOTS + 1)
    ]

app_ui = ui.page_fluid(
    ui.panel_title("Dynamic number of plots"),
    ui.card(
        ui.card_header("Enter parameterised SQL"),
        ui.layout_columns(
            ui.input_text_area("sql_input", label="SQL Input", value="SELECT * FROM stocks WHERE price > 5 AND {ticker, type=slider, min=1, max=10, step=1} AND {my_param, type=text_box}", rows=6, width="100%"),
            ui.output_text_verbatim("output_sql_parameters", ),
            width="100%",
            col_widths=[6, 6],
        ),
    ),
    ui.input_action_button("submit_query", "Submit Query"),
    ui.accordion(*make_items(), id="acc", multiple=True),
)

def server(input, output, session):
    parameter_universe = reactive.Value(dict())
    
    @render_widget
    def plot_1():
        return px.scatter(
            df,
            x="agg_metric_period",
            y="agg_metric_value",
            color="is_spike",
            title=f"Plot 1: Slider value is {input.slider_1()}",
        )
        
    @reactive.effect
    @reactive.event(input.submit_query)
    def _handle_submit_query():
        parameterised_sql = input.sql_input()
        parameter_universe_ = parse_parameterised_sql(parameterised_sql)
        parameter_universe.set(parameter_universe_)

        to_add = {"slider": [], "text_box": []}
        cnt = 0
        # update UI by inserting slider and text box inputs dynamically for parameters
        for param_id, param_info in parameter_universe_.items():
            cnt += 1
            if param_info.get("type") == "slider":
                to_add["slider"].append(
                    ui.input_slider(
                        f"slider_{param_id}_{cnt}",
                        label=f"Slider for {param_id}",
                        value=param_info.get("min", 1),
                        min=param_info.get("min", 1),
                        max=param_info.get("max", 10),
                        step=param_info.get("step", 1),
                    ),
                )
            elif param_info.get("type") == "text_box":
                to_add["text_box"].append(
                    ui.input_text(
                        f"text_box_{param_id}_{cnt}",
                        label=f"Text box for {param_id}",
                        value=param_info.get("default", ""),
                    ),
                )
            
        ui.insert_ui(
            ui=to_add["text_box"],
            selector="#input_card_1",
            session=session,
        )
        ui.insert_ui(
            ui=to_add["slider"],
            selector="#input_card_1",
            session=session,
        )

    @render.text
    def output_sql_parameters():
        parameter_universe_ = parameter_universe.get()
        return str(parameter_universe_) if parameter_universe_ else "No parameters found in SQL input."
    

app = App(app_ui, server)
