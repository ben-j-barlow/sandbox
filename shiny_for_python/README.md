# Shiny for Python

This was produced whilst learning how to build a Databricks-hosted app that reads from Unity Catalog. Notes are therefore tailored to his app.

## Decorators

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

## Dynamic UI

