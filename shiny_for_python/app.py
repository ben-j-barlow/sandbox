# Save this as app.py and run with: shiny run app.py --reload

import matplotlib.pyplot as plt
import numpy as np
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

# 1. Generate data function using numpy
def generate_static_plot_data():
    """Generates a simple x, y dataset."""
    np.random.seed(42) # for reproducibility
    x = np.random.rand(30) * 10
    y = np.random.rand(30) * 10
    return x, y

# 2. Define the application UI
app_ui = ui.page_fluid(
    ui.h3("Dynamically Inserted Matplotlib Plots"),
    ui.input_action_button("add_plot_button", "Add New Plot", class_="btn-primary mb-3"),
    ui.div(id="plots_host_div")  # This div will host the dynamically inserted plots
)

# 3. Define the server logic
def server(input: Inputs, output: Outputs, session: Session):
    # Generate data once when the session starts; all plots will use this data
    plot_data_x, plot_data_y = generate_static_plot_data()

    @reactive.effect
    @reactive.event(input.add_plot_button)
    def handle_add_plot():
        # input.add_plot_button() returns the number of times the button has been clicked.
        # This serves as a unique identifier for each new plot.
        plot_num = input.add_plot_button()
        
        plot_ui_id = f"dynamic_plot_{plot_num}"
        # Create an ID for the div that will wrap this specific plot and its title
        plot_wrapper_id = f"plot_wrapper_{plot_num}"

        print(f"Button clicked. Attempting to add plot UI with ID: {plot_ui_id}") # For logging

        # # Define the UI for the new plot (a heading and the plot output area)
        new_plot_ui_element = ui.div(
            ui.hr(), # Add a horizontal rule for separation
            ui.h5(f"Plot Number {plot_num}"),
            id=plot_wrapper_id # Give the wrapper div an ID
        )

        # # Insert the new plot's UI into the host div [1]
        ui.insert_ui(
            ui=new_plot_ui_element,
            selector="#plots_host_div",
            where="beforeEnd"  # Inserts inside the element, after its last child
        )

        # # Now, dynamically create and register the render function for this new plot.
        # # We use a factory function to correctly capture the plot_num for each renderer.
        # def renderer_factory(current_plot_number, current_plot_id_str):
        #     def _render_specific_plot():
        #         print(f"Rendering plot for UI ID: {current_plot_id_str}") # For logging
        #         fig, ax = plt.subplots()
        #         ax.scatter(plot_data_x, plot_data_y, label=f"Data Points", color=f"C{current_plot_number % 10}")
        #         ax.set_title(f"Plot {current_plot_number}")
        #         ax.set_xlabel("X Values")
        #         ax.set_ylabel("Y Values")
        #         ax.legend()
        #         # To make plots slightly different, you could vary something based on current_plot_number
        #         # For example, change marker size or add a line:
        #         if current_plot_number > 1:
        #             ax.plot(plot_data_x, np.array(plot_data_y) * (1 + current_plot_number * 0.05), linestyle='--', color='grey', alpha=0.5)
        #         return fig
        #     return _render_specific_plot

        # # Create the specific render function for the current plot_num
        # specific_plot_renderer = renderer_factory(plot_num, plot_ui_id)

        # # Apply the @render.plot decorator's functionality manually.
        # # render.plot() returns an object (a PlotRenderer instance) that Shiny can use.
        # final_renderer_object = render.plot(specific_plot_renderer)

        # # Register this renderer with the current session.
        # # This makes Shiny aware that it needs to call this function
        # # to provide content for the ui.output_plot(plot_ui_id).
        # session._register_renderer(name=plot_ui_id, renderer=final_renderer_object)
        
        # print(f"Successfully registered renderer for {plot_ui_id}")


# 4. Create the App object
app = App(app_ui, server)

# To run this app:
# 1. Save the code as app.py (or any other .py file).
# 2. Open your terminal or command prompt.
# 3. Navigate to the directory where you saved the file.
# 4. Run the command: shiny run app.py --reload