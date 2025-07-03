import numpy as np
from shiny import ui, render, App, module, reactive, req
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
import asyncio
import re
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_QUERY = "SELECT * FROM stocks WHERE price > 5 AND my_var = {my_var, type=slider, min=1, max=10, step=1} AND {row_condition, type=text_box}"

try:
    from databricks import sql

    SERVER_HOSTNAME = os.getenv("SERVER_HOSTNAME")
    SQL_WAREHOUSE_ID = os.getenv("SQL_WAREHOUSE_ID")
    SQL_USER_TOKEN = os.getenv("SQL_USER_TOKEN")
except (KeyError, ImportError) as e:
    SERVER_HOSTNAME = None
    SQL_WAREHOUSE_ID = None
    SQL_USER_TOKEN = None


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


def parse_parameterised_sql(sql) -> set[ParamConfig]:
    matches = set(re.findall(r"\{(.*?)\}", sql))
    parameter_universe = list()

    for match in matches:
        parts = [p.strip() for p in match.split(",")]
        param_id = parts[0]
        param_properties = {ele.split("=")[0]: ele.split("=")[1] for ele in parts[1:]}
        try:
            if param_properties["type"] == "slider":
                try:
                    param_config = SliderParamConfig(
                        param_id=param_id,
                        sql_identifier=append_parenthesis(match),
                        min_val=param_properties["min"],
                        max_val=param_properties["max"],
                        step=param_properties["step"],
                        default=param_properties.get("default", None),
                    )
                except KeyError as e:
                    raise ValueError(
                        f"Parameter '{param_id}' is missing required properties: {e}"
                    )
            elif param_properties["type"] == "text_box":
                try:
                    param_config = TextBoxParamConfig(
                        param_id=param_id,
                        sql_identifier=append_parenthesis(match),
                        default=param_properties.get("default", None),
                    )
                except KeyError as e:
                    raise ValueError(
                        f"Parameter '{param_id}' is missing required properties: {e}"
                    )
            else:
                raise ValueError(
                    f"Unsupported parameter type '{param_properties['type']}' for parameter '{param_id}'."
                )
        except KeyError as e:
            raise ValueError(f"Parameter '{param_id}' is missing 'type' property.")

        parameter_universe.append(param_config)
    return parameter_universe


df_columns = ["agg_metric_period", "agg_metric_value", "is_spike"]
df = pd.DataFrame(
    {
        "agg_metric_period": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "agg_metric_value": np.random.rand(10) * 100,
        "is_spike": [
            False,
            False,
            True,
            False,
            False,
            True,
            False,
            False,
            False,
            False,
        ],
    }
)


def append_parenthesis(match: str) -> str:
    "Append {} parentheses at start and finish."
    return "{" + match + "}"


def get_plot_input_id(param_id: str, param_type: str) -> str:
    """Generate a unique input ID for a plot parameter."""
    return f"input_{param_type}_{param_id}"


def execute_query(connection, statement, max_rows=10000):
    """
    Executes an SQL statement and fetches up to `max_rows` results.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(statement)
            res = (
                cursor.fetchmany_arrow(max_rows)
                if max_rows
                else cursor.fetchall_arrow()
            )
        return res
    except Exception as e:
        print(f"Error executing query: {e}")
        return e


app_ui = ui.page_fluid(
    ui.panel_title("Dynamic number of plots"),
    ui.card(
        ui.card_header("Enter parameterised SQL"),
        ui.layout_columns(
            ui.input_text_area(
                "sql_input",
                label="SQL Input",
                value=INITIAL_QUERY,
                rows=6,
                width="100%",
            ),
            ui.output_text_verbatim(
                "output_sql_parameters",
            ),
            width="100%",
            col_widths=[6, 6],
        ),
    ),
    ui.input_action_button("submit_query", "Submit Query"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Plot"),
            output_widget("display_plot", width="100%", height="400px"),
            id="plot_card",
            full_screen=True,
        ),
        ui.navset_card_tab(
            ui.nav_panel(
                "Input",
                ui.TagList(
                    ui.input_task_button(id=f"run_query", label="Run Query"),
                    ui.output_ui("user_input_ui_components"),
                ),
            ),
            ui.nav_panel(
                "Query",
                ui.output_text("display_query"),
            ),
        ),
        width="100%",
        col_widths=[8, 4],
    ),
)


def server(input, output, session):
    parameter_universe = reactive.Value(list())
    parameterised_sql = reactive.Value("")

    # Define the extended task to execute the query asynchronously
    @ui.bind_task_button(button_id="run_query")
    @reactive.extended_task
    async def run_query_task(query: str):
        if SERVER_HOSTNAME and SQL_WAREHOUSE_ID and SQL_USER_TOKEN:
            try:
                # Connect to SQL warehouse inside the task to ensure thread safety
                connection = sql.connect(
                    server_hostname=SERVER_HOSTNAME,
                    http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
                    user_token=SQL_USER_TOKEN,
                    session_configuration={"STATEMENT_TIMEOUT": "60"},
                )
                res = await asyncio.to_thread(execute_query, connection, query)
                ui.update_action_button("cancel_query", disabled=True)
                return res
            except Exception as e:
                return e
        else:
            return df

    @reactive.event(input.run_query)
    def handle_run_query():
        run_query_task(compile_query())

    @reactive.calc
    def compile_query():
        parameter_universe_ = parameter_universe.get()
        if not parameter_universe_:
            return ""

        # build {param_identifier: value} dict
        for_replace = {
            ele.sql_identifier: str(
                getattr(input, get_plot_input_id(ele.param_id, ele.param_type))()
            )
            for ele in parameter_universe_
        }

        # use {param_identifier: value} dict to compile the query
        pattern = re.compile("|".join(map(re.escape, for_replace.keys())))
        compiled_query = pattern.sub(
            lambda match: for_replace[match.group(0)], req(parameterised_sql.get())
        )
        return compiled_query

    @render_widget
    @reactive.event(input.run_query)
    def display_plot():
        return px.scatter(
            df,
            x="agg_metric_period",
            y="agg_metric_value",
            color="is_spike",
            title=f"Plot 1",
        )

    @render.text
    def display_query():
        to_display = compile_query()
        if not to_display:
            return "Nothing to display. Please run a query first."
        return to_display

    @render.ui
    @reactive.event(parameter_universe)
    def user_input_ui_components():
        to_return = ui.TagList()
        parameter_universe_ = parameter_universe.get()
        for param_config in parameter_universe_:
            param_id = param_config.param_id

            if isinstance(param_config, SliderParamConfig):
                to_return.append(
                    ui.input_slider(
                        get_plot_input_id(param_id, param_config.param_type),
                        label=param_id,
                        value=param_config.default,
                        min=param_config.min_val,
                        max=param_config.max_val,
                        step=param_config.step,
                    )
                )
            elif isinstance(param_config, TextBoxParamConfig):
                to_return.append(
                    ui.input_text(
                        get_plot_input_id(param_id, param_config.param_type),
                        label=param_id,
                        value=param_config.default,
                    )
                )
        return to_return

    @reactive.effect
    @reactive.event(input.submit_query)
    def _parse_parameterised_sql():
        parameterised_sql.set(input.sql_input())
        parameter_universe_ = parse_parameterised_sql(parameterised_sql.get())
        parameter_universe.set(parameter_universe_)

    @render.text
    def output_sql_parameters():
        parameter_universe_ = parameter_universe.get()
        if parameter_universe_:
            return "\n".join([ele.param_id for ele in parameter_universe_])
        return "No parameters found in SQL input."


app = App(app_ui, server)
