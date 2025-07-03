import matplotlib.pyplot as plt
import numpy as np
from shiny import ui, render, App, module, reactive
from shinywidgets import render_plotly, output_widget, render_widget
from datetime import datetime
import pandas as pd
import plotly.express as px
import re
from dataclasses import dataclass
from abc import ABC
from numbers import Real

PLOTS = 1

def parse_parameterised_sql(sql) -> set[ParamConfig]:
    matches = set(re.findall(r'\{(.*?)\}', sql))
    parameter_universe = list()

    for match in matches:
        parts = [p.strip() for p in match.split(',')]
        param_id = parts[0]
        param_properties = {ele.split('=')[0]: ele.split('=')[1] for ele in parts[1:]}
        try:
            if param_properties['type'] == 'slider':
                try:
                    param_config = SliderParamConfig(
                        param_id=param_id,
                        sql_identifier=match,
                        min_val=param_properties['min'],
                        max_val=param_properties['max'],
                        step=param_properties['step'],
                        default=param_properties.get('default', None),
                    )
                except KeyError as e:
                    raise ValueError(f"Parameter '{param_id}' is missing required properties: {e}")
            elif param_properties['type'] == 'text_box':
                try:
                    param_config = TextBoxParamConfig(
                        param_id=param_id,
                        sql_identifier=match,
                        default=param_properties.get('default', None),
                    )
                except KeyError as e:
                    raise ValueError(f"Parameter '{param_id}' is missing required properties: {e}")
            else:
                raise ValueError(f"Unsupported parameter type '{param_properties['type']}' for parameter '{param_id}'.")
        except KeyError as e:
            raise ValueError(f"Parameter '{param_id}' is missing 'type' property.")        
        
        
        parameter_universe.append(param_config)
    return parameter_universe


df_columns = ["agg_metric_period", "agg_metric_value", "is_spike"]
df = pd.DataFrame(
    {
        "agg_metric_period": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "agg_metric_value": np.random.rand(10) * 100,
        "is_spike": [False, False, True, False, False, True, False, False, False, False],
    }
)



@dataclass
class ParamConfig(ABC):
    """Base parameter configuration using a dataclass."""
    param_id: str
    sql_identifier: str


@dataclass
class SliderParamConfig(ParamConfig):
    """Slider configuration inheriting from the base dataclass."""

    min_val: float
    max_val: float
    step: float
    # Use a field with a default_factory to handle the mutable default logic
    default: float
    
    def __post_init__(self):
        """Called after the dataclass's own __init__."""
        self.min_val = float(self.min_val)
        self.max_val = float(self.max_val)
        self.step = float(self.step)

        if self.default is None:
            self.default = self.min_val

@dataclass
class TextBoxParamConfig(ParamConfig):
    """Text box configuration inheriting from the base dataclass."""
    default: str

    def __post_init__(self):
        """Called after the dataclass's own __init__."""
        if self.default is None:
            self.default = ""
        self.default = str(self.default)

def get_plot_input_id(plot_id: int, param_id: str, param_type: str) -> str:
    """Generate a unique input ID for a plot parameter."""
    return f"input_plot_{plot_id}_{param_type}_{param_id}"

def get_plot_input_div_id(plot_id: int, param_id: str, param_type: str) -> str:
    """Generate a unique input ID for a plot parameter."""
    return f"div_{get_plot_input_id(plot_id, param_id, param_type)}"

def get_selector_for_plot_input_removal(plot_id: int) -> str:
    """Generate a selector for removing all input elements for a specific plot."""
    #$('div[id^="div_input_plot_1_"]')
    return f'div[id^="div_input_plot_{plot_id}"]'

def get_param_type_from_class_name(class_name: str) -> str:
    """Get the parameter type from the class name."""
    if class_name == "SliderParamConfig":
        return "slider"
    elif class_name == "TextBoxParamConfig":
        return "text_box"
    else:
        raise ValueError(f"Unsupported parameter class name: {class_name}")
    
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
                    ui.input_action_button(id=f"run_query_{i}", label="Run Query"),
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
    ui.input_action_button("remove_ui", "Remove UI"),
    ui.accordion(*make_items(), id="acc", multiple=True),
)

def server(input, output, session):
    parameter_universe = reactive.Value(list())
    
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
    @reactive.event(input.run_query_1)
    def _handle_run_query_1():
        parameter_universe_ = parameter_universe.get()
        
    @reactive.effect
    @reactive.event(input.remove_ui)
    def _handle_remove_ui():
        ui.remove_ui(selector=get_selector_for_plot_input_removal(plot_id=1), session=session, multiple=True)

    @reactive.effect
    @reactive.event(input.submit_query)
    def _handle_submit_query():
        # Parse the parameterised SQL input
        parameterised_sql = input.sql_input()
        parameter_universe_ = parse_parameterised_sql(parameterised_sql)
        parameter_universe.set(parameter_universe_)

        
        # Add new UI components based on the parsed parameters
        
        cnt = 0
        for param_config in parameter_universe_:
            cnt += 1
            param_id = param_config.param_id

            if isinstance(param_config, SliderParamConfig):
                param_type = "slider"
                to_add = ui.input_slider(
                    get_plot_input_id(1, param_id, param_type),
                    label=param_id,
                    value=param_config.default,
                    min=param_config.min_val,
                    max=param_config.max_val,
                    step=param_config.step,
                )
            elif isinstance(param_config, TextBoxParamConfig):                
                param_type = "text_box"
                to_add = ui.input_text(
                    get_plot_input_id(1, param_id, param_type),
                    label=param_id,
                    value=param_config.default,
                )
                
            ui.insert_ui(
                ui=ui.div(to_add, id=get_plot_input_div_id(plot_id=1, param_id=param_id, param_type=param_type)),
                selector="#input_card_1",
                session=session,
            )

    @render.text
    def output_sql_parameters():
        parameter_universe_ = parameter_universe.get()
        if parameter_universe_:
            return "\n".join([ele.param_id for ele in parameter_universe_])
        return "No parameters found in SQL input."
    

app = App(app_ui, server)
