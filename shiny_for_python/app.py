import matplotlib.pyplot as plt
import numpy as np
from shiny import ui, render, req, App, module, reactive

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
            ui.input_action_button("add_plot_button", "Add plot"),
            ui.output_text_verbatim("current_plot_count_display"),
            width=250 # Optional: give sidebar a consistent width
        ),
        # Main panel to display all plots
        ui.output_ui("plots"),
    ),
)

MAX_PLOTS = 5


def server(input, output, session):
    # Reactive value to store the current number of plots
    current_n_plots = reactive.Value(1) # Start with 1 plot

    @reactive.effect
    @reactive.event(input.add_plot_button)
    def _handle_add_plot_click():
        # Only add a plot if the current number is less than MAX_PLOTS
        if current_n_plots.get() < MAX_PLOTS:
            current_n_plots.set(current_n_plots.get() + 1)
        if current_n_plots.get() == MAX_PLOTS:
            ui.update_action_button(
                "add_plot_button",
                session=session,
                label="Max plots reached",
                disabled=True
            )

    # Function to dynamically render UI components (plots)
    @render.ui
    def plots():
        # Ensure value is an integer and available
        #n_plots = int(req(input.n_plots()))
        n_plots = current_n_plots.get()
        # Dynamically create server-side functions for each plot
        for i in range(1, n_plots + 1):
            plot_server(f"plot_{i}", plot_id=i, max_plots=MAX_PLOTS)
        # Dynamically create UI components for each plot
        # Note that the names must match the server-side functions
        # But they're close to each other in code
        return ([plot_ui(f"plot_{i}") for i in range(1, n_plots + 1)],)


app = App(app_ui, server)