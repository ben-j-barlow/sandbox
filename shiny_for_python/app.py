import matplotlib.pyplot as plt
import numpy as np
from shiny import ui, render, req, App, module

MAX_PLOTS = 5


# UI module for a single plot
@module.ui
def plot_ui():
    # Returns a placeholder for a plot that will be rendered server-side
    return ui.output_plot("plot")


# Server module to generate and render each plot
@module.server
def plot_server(input, output, session, plot_id: int, max_plots: int = MAX_PLOTS):
    @render.plot
    def plot():
        # Generate data for the plot based on the plot_id
        x = np.r_[1 : (plot_id + 1)]
        y = np.r_[1 : (plot_id + 1)]

        fig, ax = plt.subplots()
        ax.scatter(x, y)
        ax.set_xlim(0, max_plots)
        ax.set_ylim(0, max_plots)
        ax.set_title(f"1: {plot_id}. n is {max_plots}")
        return fig


app_ui = ui.page_fluid(
    ui.panel_title("Dynamic number of plots"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider(
                "n_plots", "Number of plots", value=1, min=1, max=MAX_PLOTS
            ),
        ),
        # Main panel to display all plots
        ui.output_ui("plots"),
    ),
)


def server(input, output, session):
    # Function to dynamically render UI components (plots)
    @render.ui
    def plots():
        # Ensure value is an integer and available
        n_plots = int(req(input.n_plots()))
        # Dynamically create server-side functions for each plot
        for i in range(1, n_plots + 1):
            plot_server(f"plot_{i}", plot_id=i, max_plots=MAX_PLOTS)
        # Dynamically create UI components for each plot
        # Note that the names must match the server-side functions
        # But they're close to each other in code
        return ([plot_ui(f"plot_{i}") for i in range(1, n_plots + 1)],)


app = App(app_ui, server)