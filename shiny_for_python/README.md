# Shiny for Python

This was produced whilst learning how to build a Databricks-hosted app that reads from Unity Catalog. Notes are therefore tailored to his app.

## General

* [R Shiny to Shiny for Python Guide](https://gist.github.com/wch/616934a6fe57636434154c112ac8a718)
* [Using AI well](https://www.appsilon.com/post/shiny-vscode-copilot)
* [UI Guide (Shiny Express)](https://shiny.posit.co/py/docs/user-interfaces.html)
* [Reactive file reading](https://shiny.posit.co/py/docs/reactive-patterns.html#file)
* [Collapsable tabs](https://shiny.posit.co/py/api/core/ui.accordion_panel.html#shiny.ui.accordion_panel)

## Useful Decorators

* `@reactive.effect`: Function automatically re-runs whenever any of the reactive values it reads inside its body change. Great for **triggering a database query** (to Unity Catalog).
* `@reactive.event`: Similar to `effect` but only re-runs when the specific reactive values (or input functions) passed as arguments to the decorator change. Example usage: `@reactive.event(input.submit_query)`.

Usage of the above. `@reactive.event(...)` takes precedence for triggering. The outer `@reactive.effect` still ensures that handle_query runs within a reactive context, allowing the function to correctly read the current values of any reactive sources, like `input.sql_query()`.

```
@reactive.effect
@reactive.event(input.submit_query, input.submit_query_viz_btn, input.window_sz_entry, input.sigma_th_entry)
def handle_query():
    ui.update_action_button("cancel_query", disabled=False)
    # Don't attempt execution for empty queries
    if not input.sql_query().strip():
        ui.notification_show("Please enter a SQL query.", type="warning")
        return
    
    query = compile_query(input)
    run_query_task(query)
```

* `@reactive.isolate`: Create a non-reactive scope within a reactive scope. Prevents triggering. Imagine controling the title of a plot through a text box, but you don't want to re-run the plot generation upon changing the title. Inside the `@reactive.effect` that generates the Plotly figure use `title = reactive.isolate(input.plot_title)`.
* `@reactive.extended_task`: Call like a regular function. Designed for long-running processes, without freezing the UI. Highly relevant for queries running in the background.

# Useful Functions / Tips

* [req](https://shiny.posit.co/r/reference/shiny/0.14/req.html)
* use `ui.input_task_button` instead of `ui.input_action_button` to invoke an extended task task, since the former automatically prevents subsequent clicks until the task completes
* linking multiple Plotly plots (see NBA Dashboard in Gallery)
* nice layout (see Stock Explorer Dashboard in Gallery)

## Dynamic UI, Plots and Modules

* [Beyond R Shiny: Shiny for Python's Clean Design for Dynamic Plot Management](https://www.appsilon.com/post/shiny-for-python-clean-design-for-dynamic-plot-management)
* [Dynamic UI Docs](https://shiny.posit.co/py/api/express/express.ui.panel_conditional.html)
* [How to use modules](https://www.appsilon.com/post/shiny-for-python-custom-module)

## Understanding Non Blocking Tasks

Main docs are [here](https://shiny.posit.co/py/docs/nonblocking.html#:~:text=Shiny%20has%20async%20support%20as,parts%20of%20your%20Shiny%20app).