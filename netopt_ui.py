import ipywidgets as widgets
from IPython.display import display, clear_output


def parse(txt):
    return eval(txt) if txt.strip() else None


def run_netopt(_):
    with output:
        clear_output()
        try:
            params = {
                "num_warehouses": num_wh.value,
                "warehouses": warehouses,
                "customers": customers,
                "distance": distance,
                "distance_ranges": parse(distance_ranges.value),
                "objective": objective.value,
            }
        except Exception as excp:
            raise excp
        print("Parameters:", params)
        # Here you would call your netopt function with the parameters
        # For example:
        # result = netopt(num_warehouses=num_wh.value, ...)
        # print(result)


def netopt_ui(warehouses: dict, customers: dict, distance: dict):
    """User interface for the netopt function."""

    # Define a consistent layout for all form elements
    form_layout = widgets.Layout(
        width="100%"  # Full width for the widget itself
    )

    # Define a consistent style for all form elements
    form_style = {"description_width": "200px"}  # Fixed width for all descriptions

    # Use a longer description width to prevent truncation
    # wide_desc = widgets.Layout(width="100%", description_width="150px")

    objective = widgets.Dropdown(
        options=["-", "p-median", "UFLP", "CFLP"],
        description="Problem type",
        layout=form_layout,
        style=form_style,
    )

    num_wh = widgets.IntSlider(
        description="# Warehouses (for p-median)",
        min=1,
        max=20,
        value=3,
        layout=form_layout,
        style=form_style,
        # style={"description_width": "initial"},  # Prevents truncation
    )

    distance_ranges = widgets.Text(
        description="Dist. Ranges",
        placeholder="[0, 10, 20]",
        layout=form_layout,
        style=form_style,
    )

    button = widgets.Button(
        description="Solve",
        button_style="success",
    )

    output = widgets.Output()

    # def on_run(_):
    #     with output:
    #         print("Button clicked.")
    #         run_netopt()

    button.on_click(run_netopt)

    sec_layout = widgets.Layout(
        border="1px solid #ddd", padding="10px", margin="5px", width="48%"
    )

    # Section 1: General parameters
    sec1 = widgets.VBox(
        [
            widgets.HTML("<h4>General</h4>"),
            objective,
            num_wh,
            distance_ranges,
            # warehouses,
            # customers,
            # distance,
            # distance_ranges,
            # objective,
        ],
        layout=sec_layout,
    )

    #     # Section 2: Constraints
    sec2 = widgets.VBox(
        [
            widgets.HTML("<h4>Constraints</h4>"),
            # high_sd,
            # avg_sd,
            # max_sd,
            # unit_cost,
            # force_open,
            # force_closed,
            # force_alloc,
            # mut_excl,
            # force_single,
            # force_uncap,
        ],
        layout=sec_layout,
    )

    # Section 3: Display & run
    # sec3 = widgets.VBox(
    #     [
    #         # widgets.HTML("<h4>Display & Run</h4>"),
    #         # ignore_fc,
    #         # plot,
    #         # plot_size,
    #         # hide_inactive,
    #         # hide_flows,
    #         # solver_log,
    #         # run_button,
    #     ],
    #     layout=sec_layout,
    # )

    # Combine into one HBox
    ui = widgets.HBox([sec1, sec2])

    display(ui, button, output)


# def netopt_ui(warehouses, customers, distance):

#     # --- 1. Define all your widgets ---
#     # warehouses = widgets.Textarea(description="Warehouses", placeholder="['W1','W2','W3']")
#     # customers  = widgets.Textarea(description="Customers",  placeholder="['C1','C2','C3']")
#     # distance   = widgets.Textarea(description="Distance",   placeholder="[[10,20],[5,15]]")
#     # distance_ranges = widgets.Text(description="Dist. Ranges", placeholder="[0,10,20]")

#     # objective = widgets.Dropdown(
#     #     options=["", "mindistance", "maxcover"], description="Objective"
#     # )
#     # high_sd = widgets.FloatText(description="High svc dist")
#     # avg_sd = widgets.FloatText(description="Avg svc dist")
#     # max_sd = widgets.FloatText(description="Max svc dist")
#     # unit_cost = widgets.FloatText(description="Unit cost", value=0.1)

#     # force_open = widgets.Text(description="Force open", placeholder="[0,2]")
#     # force_closed = widgets.Text(description="Force closed", placeholder="[1]")
#     # force_alloc = widgets.Text(description="Force allocs", placeholder="[(0,1)]")
#     # mut_excl = widgets.Text(description="Mut. excl.", placeholder="[(0,1)]")
#     # force_single = widgets.Checkbox(description="Single sourcing", value=True)
#     # force_uncap = widgets.Checkbox(description="Uncapacitated", value=False)

#     # ignore_fc = widgets.Checkbox(description="Ignore fixed cost")
#     # plot = widgets.Checkbox(description="Show plot", value=True)
#     # plot_size = widgets.Text(description="Plot size", placeholder="(8,12)")
#     # hide_inactive = widgets.Checkbox(description="Hide inactive")
#     # hide_flows = widgets.Checkbox(description="Hide flows")
#     # solver_log = widgets.Checkbox(description="Solver log")

#     run_button = widgets.Button(description="Run netopt", button_style="success")
#     out = widgets.Output()

#     # --- 2. Simple eval helper ---
#     def parse(txt):
#         return eval(txt) if txt.strip() else None

#     # --- 3. Callback to call netopt ---
#     def on_run(_):
#         with out:
#             clear_output()
#             # try:
#             #     params = {
#             #         "num_warehouses": num_wh.value,
#             #         "warehouses": warehouses,
#             #         "customers": customers,
#             #         "distance": distance,
#             #         # "distance_ranges": parse(distance_ranges.value),
#             #         # "objective": objective.value,
#             #         # "high_service_distance": high_sd.value or None,
#             #         # "avg_service_distance": avg_sd.value or None,
#             #         # "max_service_distance": max_sd.value or None,
#             #         # "force_open": parse(force_open.value),
#             #         # "force_closed": parse(force_closed.value),
#             #         # "force_single_sourcing": force_single.value,
#             #         # "force_uncapacitated": force_uncap.value,
#             #         # "force_allocations": parse(force_alloc.value),
#             #         # "ignore_fixed_cost": ignore_fc.value,
#             #         # "plot": plot.value,
#             #         # "plot_size": parse(plot_size.value) or (8, 12),
#             #         # "hide_inactive": hide_inactive.value,
#             #         # "hide_flows": hide_flows.value,
#             #         # "solver_log": solver_log.value,
#             #         # "unit_transport_cost": unit_cost.value,
#             #         # "mutually_exclusive": parse(mut_excl.value),
#             #     }
#             #     # result = netopt(**params)
#             #     # print("Result:", result)
#             # except Exception as e:
#             #     print("Error:", e)

#     run_button.on_click(on_run)

#     # --- 4. Build three columns ---
#     sec_layout = widgets.Layout(
#         border="1px solid #ddd", padding="10px", margin="5px", width="30%"
#     )

#     # Section 1: General parameters
#     sec1 = widgets.VBox(
#         [
#             widgets.HTML("<h4>General</h4>"),
#             num_wh,
#             warehouses,
#             customers,
#             distance,
#             # distance_ranges,
#             # objective,
#         ],
#         layout=sec_layout,
#     )

#     # Section 2: Constraints
#     sec2 = widgets.VBox(
#         [
#             # widgets.HTML("<h4>Constraints</h4>"),
#             # high_sd,
#             # avg_sd,
#             # max_sd,
#             # unit_cost,
#             # force_open,
#             # force_closed,
#             # force_alloc,
#             # mut_excl,
#             # force_single,
#             # force_uncap,
#         ],
#         layout=sec_layout,
#     )

#     # Section 3: Display & run
#     sec3 = widgets.VBox(
#         [
#             # widgets.HTML("<h4>Display & Run</h4>"),
#             # ignore_fc,
#             # plot,
#             # plot_size,
#             # hide_inactive,
#             # hide_flows,
#             # solver_log,
#             # run_button,
#         ],
#         layout=sec_layout,
#     )

#     # Combine into one HBox
#     ui = widgets.HBox([sec1, sec2, sec3])
#     display(ui, out)
