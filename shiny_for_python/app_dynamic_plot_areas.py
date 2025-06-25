from shiny import reactive
from shiny.express import module, render, ui
import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass
from abc import ABC
import logging
import re


logging.basicConfig(level=logging.INFO, format='%(message)s')

logger = logging.getLogger(__name__)

# @dataclass
# class ParamConfig(ABC):
#     """Base parameter configuration using a dataclass."""
#     name: str
#     sql_identifier: str

# @dataclass
# class SliderParamConfig(ParamConfig):
#     """Slider configuration inheriting from the base dataclass."""
#     min_val: int
#     max_val: int
#     step: int
#     # Use a field with a default_factory to handle the mutable default logic
#     value: int = None

#     def __post_init__(self):
#         """Called after the dataclass's own __init__."""
#         if self.value is None:
#             self.value = self.min_val

# s = SliderParamConfig(name="slider1", sql_identifier="", min_val=1, max_val=10, step=1)

global_query = "SELECT :num"

def compile_query(global_query_sql, param):
    # query = re.sub(r"\s+", " ", global_query_sql)
    # for_replace = {f":{ele.sql_identifier}": ele.value for ele in params}
    # pattern = re.compile("|".join(map(re.escape, for_replace.keys())))
    # compiled_query = pattern.sub(lambda match: for_replace[match.group(0)], query)
    # return compiled_query
    return f"SELECT {str(param)}"

@module
def plot_area(input, output, session):
    # get starting values of parameters
    #   use defaults
    # e.g. count = reactive.value(starting_value)
    
    query = reactive.value(compile_query(global_query, input.slider))

    mult = reactive.value(1)
    # add sliders and text boxes as requested by user
    # e.g. ui.input_action_button("btn", "Increment")
    
    # if isinstance(param, SliderParamConfig):
    # ui.input_slider(id=f"input_slider_{param.name}", min=param.min_val, max=param.max_val, value=param.value, step=param.step, label=f"Control {param.name}")
    ui.input_slider(id=f"slider", min=1, max=2, value=1, step=1, label=f"Control XX")

    with ui.div():
        # render the plot
        @render.plot
        def plot():
            # Generate data for the plot based on the plot_id
            x = np.r_[1 : (2 + 1)]
            y = np.r_[1 : (2 + 1)] * mult.get()

            fig, ax = plt.subplots()
            ax.scatter(x, y)
            ax.set_title(f"mult is {mult.get()}")
        
    # update the plot depending on buttons
    @reactive.effect
    def increment():
        # query.set(compile_query(global_query, input.slider.get()))
        mult.set(input.slider.get())

plot_area("one")
ui.hr()
plot_area("two")
