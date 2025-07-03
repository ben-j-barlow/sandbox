import matplotlib.pyplot as plt
import numpy as np
from shiny import ui, render, App, module, reactive, req
from shinywidgets import render_plotly, output_widget, render_widget
from datetime import datetime
import pandas as pd
import plotly.express as px
import re
from dataclasses import dataclass
from abc import ABC, abstractmethod
from numbers import Real
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLOTS = 1
INITIAL_QUERY = "SELECT * FROM stocks WHERE price > 5 AND my_var = {my_var, type=slider, min=1, max=10, step=1} AND {row_condition, type=text_box}"

@dataclass
class ParamConfig(ABC):
    """Base parameter configuration using a dataclass."""
    param_id: str
    sql_identifier: str

    @property
    @abstractmethod
    def param_type(self) -> str:
        """Abstract property to be implemented by subclasses."""
        pass

@dataclass
class SliderParamConfig(ParamConfig):
    """Slider configuration inheriting from the base dataclass."""

    min_val: float
    max_val: float
    step: float
    # Use a field with a default_factory to handle the mutable default logic
    default: float
    param_type: str = "slider"
    
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
    param_type: str = "text_box"

    def __post_init__(self):
        """Called after the dataclass's own __init__."""
        if self.default is None:
            self.default = "xyz = 2"
        self.default = str(self.default)


def compile_query(input, parameter_universe: list[ParamConfig], plot_id: int, parameterised_query: str):
    # build {param_identifier: value} dict
    for_replace = {ele.sql_identifier: str(getattr(input, get_plot_input_id(plot_id, ele.param_id, ele.param_type))()) for ele in parameter_universe}
    
    # use {param_identifier: value} dict to compile the query
    pattern = re.compile("|".join(map(re.escape, for_replace.keys())))
    compiled_query = pattern.sub(lambda match: for_replace[match.group(0)], parameterised_query)
    return compiled_query

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
                        sql_identifier=append_parenthesis(match),
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
                        sql_identifier=append_parenthesis(match),
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

def append_parenthesis(match: str) -> str:
    "Append {} parentheses at start and finish."    
    return "{" + match + "}"

def get_plot_input_id(plot_id: int, param_id: str, param_type: str) -> str:
    """Generate a unique input ID for a plot parameter."""
    return f"input_plot_{plot_id}_{param_type}_{param_id}"

def get_plot_input_div_id(plot_id: int, param_id: str, param_type: str) -> str:
    """Generate a unique input ID for a plot parameter."""
    return f"div_{get_plot_input_id(plot_id, param_id, param_type)}"

def get_selector_for_plot_input_removal(plot_id: int) -> str:
    """Generate a selector for removing all input elements for a specific plot."""
    return f'div[id^="div_input_plot_{plot_id}"]'
    
def make_items():
    return [
        ui.accordion_panel(
            f"Section {i}",                   
            ui.layout_columns(
                ui.card(
                    ui.card_header(f"Plot {i}"),
                    ui.TagList(
                        output_widget(f"plot_{i}_plot"),
                        ui.output_text(f"plot_{i}_query"),
                    ),
                    full_screen=True,
                ),
                ui.card(
                    ui.card_header("Input"),
                    ui.input_action_button(id=f"run_query_{i}", label="Run Query"),
                    ui.output_ui("user_input_ui_components"),
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
            ui.input_text_area("sql_input", label="SQL Input", value=INITIAL_QUERY, rows=6, width="100%"),
            ui.output_text_verbatim("output_sql_parameters", ),
            width="100%",
            col_widths=[6, 6],
        ),
    ),
    ui.input_action_button("submit_query", "Submit Query"),
    ui.accordion(*make_items(), id="acc", multiple=True),
)


def server(input, output, session):
    plot_id = 1
    parameter_universe = reactive.Value(list())
    parameterised_sql = INITIAL_QUERY

    @reactive.effect
    @reactive.event(input.run_query_1)
    def _():
        parameter_universe_ = parameter_universe.get()
        compile_query(
            input,
            parameter_universe=parameter_universe_,
            plot_id=plot_id,
            parameterised_query=parameterised_sql,
        )

    @render_widget
    @reactive.event(input.run_query_1)
    def plot_1_plot():
        slider_val = getattr(input, get_plot_input_id(plot_id=1, param_id="my_var", param_type="slider"))()
        return px.scatter(
            df,
            x="agg_metric_period",
            y="agg_metric_value",
            color="is_spike",
            title=f"Plot 1: Slider value is {slider_val}",
        )
    
    @render.text
    @reactive.event(input.run_query_1)
    def plot_1_query():
        parameter_universe_ = parameter_universe.get()
        return compile_query(
            input,
            parameter_universe=parameter_universe_,
            plot_id=plot_id,
            parameterised_query=parameterised_sql,
        )

    @render.ui
    @reactive.event(parameter_universe)
    def user_input_ui_components():
        to_return = ui.TagList()
        parameter_universe_ = parameter_universe.get()
        for param_config in parameter_universe_:
            param_id = param_config.param_id

            if isinstance(param_config, SliderParamConfig):
                to_return.append(ui.input_slider(
                    get_plot_input_id(plot_id, param_id, param_config.param_type),
                    label=param_id,
                    value=param_config.default,
                    min=param_config.min_val,
                    max=param_config.max_val,
                    step=param_config.step,
                ))
            elif isinstance(param_config, TextBoxParamConfig):
                to_return.append(ui.input_text(
                    get_plot_input_id(plot_id, param_id, param_config.param_type),
                    label=param_id,
                    value=param_config.default,
                ))
        return to_return  
        
    @reactive.effect
    @reactive.event(input.submit_query)
    def _handle_submit_query():
        # Parse the parameterised SQL input
        parameterised_sql = input.sql_input()
        parameter_universe_ = parse_parameterised_sql(parameterised_sql)
        parameter_universe.set(parameter_universe_)

        
    @render.text
    def output_sql_parameters():
        parameter_universe_ = parameter_universe.get()
        if parameter_universe_:
            return "\n".join([ele.param_id for ele in parameter_universe_])
        return "No parameters found in SQL input."
    

app = App(app_ui, server)
