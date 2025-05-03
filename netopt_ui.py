import ipywidgets as widgets
from IPython.display import display, clear_output
from netopt_compat import netopt


def parse(txt):
    try:
        return eval(txt) if txt.strip() else None
    except Exception as excp:
        print(f"Error parsing input: {excp}")
        raise excp


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
        options=[
            ("p-median", "p-median"),
            ("p-cover", "p-cover"),
            ("UFLP", "UFLP"),
            ("CFLP", "CFLP"),
        ],
        description="Problem type",
        value="p-median",
        layout=form_layout,
        style=form_style,
    )

    objective_function = widgets.Dropdown(
        options=[
            ("Minimize AWD", "mindistance"),
            ("Minimize total cost", "mincost"),
        ],
        description="Func. to minimize (for p-median)",
        value="mindistance",
        layout=form_layout,
        style=form_style,
        disabled=True,
    )

    num_wh = widgets.IntSlider(
        description="# Warehouses (for p-median)",
        min=1,
        max=len(warehouses.keys()),
        value=3,
        layout=form_layout,
        style=form_style,
        disabled=True,
        # style={"description_width": "initial"},  # Prevents truncation
    )

    distance_ranges = widgets.Text(
        description="Dist. Ranges",
        placeholder="[0, 10, 20]",
        layout=form_layout,
        style=form_style,
    )

    high_service_distance = widgets.FloatText(
        description="Service radius (R for p-cover)",
        value=1000,
        layout=form_layout,
        style=form_style,
        disabled=True,
    )

    plot = widgets.Checkbox(
        description="Show plot",
        value=True,
        layout=form_layout,
        style=form_style,
    )

    plot_size = widgets.Text(
        description="Plot size",
        value="(8, 12)",
        layout=form_layout,
        style=form_style,
    )

    hide_inactive = widgets.Checkbox(
        description="Hide inactive facilities",
        layout=form_layout,
        style=form_style,
    )

    force_single_sourcing = widgets.Checkbox(
        description="Force single sourcing",
        layout=form_layout,
        style=form_style,
    )

    force_uncapacitated = widgets.Checkbox(
        description="Force uncapacitated",
        layout=form_layout,
        style=form_style,
    )

    ignore_fixed_cost = widgets.Checkbox(
        description="Ignore fixed cost",
        layout=form_layout,
        style=form_style,
    )

    force_open = widgets.Text(
        description="Force open",
        placeholder="[1, 4]",
        layout=form_layout,
        style=form_style,
    )

    force_closed = widgets.Text(
        description="Force closed",
        placeholder="[1, 4]",
        layout=form_layout,
        style=form_style,
    )

    force_allocations = widgets.Text(
        description="Force allocations",
        placeholder="[(1, 4), (2, 2)]",
        layout=form_layout,
        style=form_style,
    )

    unit_transport_cost = widgets.FloatText(
        description="Unit transport cost",
        value=0.1,
        layout=form_layout,
        style=form_style,
    )

    mutually_exclusive = widgets.Text(
        description="Mutually exclusive",
        placeholder="[(1, 2), (3, 4)]",
        layout=form_layout,
        style=form_style,
    )

    warehouse_marker = widgets.Dropdown(
        options=[
            ("Square", "s"),
            ("Circle", "o"),
            ("Star", "*"),
            ("Triangle", "^"),
            ("Inverted Triangle", "v"),
        ],
        description="Warehouse marker",
        layout=form_layout,
        style=form_style,
    )

    warehouse_markercolor = widgets.Dropdown(
        options=["red", "green", "blue", "black", "yellow"],
        description="Warehouse marker",
        layout=form_layout,
        style=form_style,
    )

    warehouse_markersize = widgets.IntSlider(
        description="Warehouse marker size",
        min=1,
        max=12,
        value=6,
        layout=form_layout,
        style=form_style,
        # style={"description_width": "initial"},  # Prevents truncation
    )

    customer_marker = widgets.Dropdown(
        options=[
            ("Square", "s"),
            ("Circle", "o"),
            ("Star", "*"),
            ("Triangle", "^"),
            ("Inverted Triangle", "v"),
        ],
        description="Customer marker",
        value="o",
        layout=form_layout,
        style=form_style,
    )

    customer_markercolor = widgets.Dropdown(
        options=["red", "green", "blue", "black", "yellow"],
        description="Customer marker",
        value="blue",
        layout=form_layout,
        style=form_style,
    )

    customer_markersize = widgets.IntSlider(
        description="Customer marker size",
        min=1,
        max=12,
        value=4,
        layout=form_layout,
        style=form_style,
        # style={"description_width": "initial"},  # Prevents truncation
    )

    button = widgets.Button(
        description="Solve",
        button_style="success",
    )

    output = widgets.Output()

    # Function to update widget states based on objective selection
    def on_objective_change(change):
        # Enable num_wh only for p-median and p-cover
        if change["new"] in ["p-median", "p-cover"]:
            num_wh.disabled = False
        else:
            num_wh.disabled = True

        if change["new"] == "p-median":
            objective_function.disabled = False
            # ignore_fixed_cost.value = True
        else:
            objective_function.disabled = True
            objective_function.value = "mindistance"

        # You can also update other widgets visibility here
        # For example, show high_service_distance only for p-cover
        if change["new"] == "p-cover":
            high_service_distance.disabled = False
        else:
            high_service_distance.disabled = True
            high_service_distance.value = 0

        if change["new"] == "UFLP":
            force_uncapacitated.value = True
            force_uncapacitated.disabled = True

        if change["new"] == "CFLP":
            force_uncapacitated.value = False
            force_uncapacitated.disabled = True

        # # For UFLP and CFLP, enable/disable appropriate options
        # if change["new"] == "mincost":
        #     force_uncapacitated.layout.display = "block"
        #     ignore_fixed_cost.layout.display = "block"
        # else:
        #     force_uncapacitated.layout.display = "none"
        #     ignore_fixed_cost.layout.display = "none"

    # Register the observer
    objective.observe(on_objective_change, names="value")

    # Trigger the function once to set initial state
    on_objective_change({"new": objective.value})

    # def on_run(_):
    #     with output:
    #         print("Button clicked.")
    #         run_netopt()
    def run_netopt(_):
        with output:
            clear_output()
            try:
                params = {
                    "num_warehouses": num_wh.value,
                    "warehouses": warehouses,
                    "customers": customers,
                    "distance": distance,
                    "plot": plot.value,
                    "plot_size": parse(plot_size.value) or (8, 12),
                    "hide_inactive": hide_inactive.value,
                    "distance_ranges": parse(distance_ranges.value) or [],
                    "objective": objective.value,
                    "objective_function": objective_function.value,
                    "unit_transport_cost": unit_transport_cost.value,
                    "high_service_distance": high_service_distance.value or None,
                    "force_single_sourcing": force_single_sourcing.value,
                    "force_uncapacitated": force_uncapacitated.value,
                    "ignore_fixed_cost": ignore_fixed_cost.value,
                    "force_open": parse(force_open.value) or [],
                    "force_closed": parse(force_closed.value) or [],
                    "force_allocations": parse(force_allocations.value) or [],
                    "mutually_exclusive": parse(mutually_exclusive.value) or [],
                    "warehouse_marker": warehouse_marker.value,
                    "warehouse_markercolor": warehouse_markercolor.value,
                    "warehouse_markersize": warehouse_markersize.value,
                    "customer_marker": customer_marker.value,
                    "customer_markercolor": customer_markercolor.value,
                    "customer_markersize": customer_markersize.value,
                }
            except Exception as excp:
                raise excp
            # print("Parameters:", params)
            # Here you would call your netopt function with the parameters
            # For example:
            if not isinstance(params.get("force_open"), list):
                print("force_open must be a list")
                return
            if not isinstance(params.get("force_closed"), list):
                print("force_closed must be a list")
                return
            if not isinstance(params.get("force_allocations"), list):
                print("force_allocations must be a list")
                return
            if not isinstance(params.get("mutually_exclusive"), list):
                print("mutually_exclusive must be a list")
                return
            if not isinstance(params.get("distance_ranges"), list):
                print("distance_ranges must be a list")
                return
            if not isinstance(params.get("plot_size"), tuple):
                print("plot_size must be a tuple")
                return

            result = netopt(
                num_warehouses=num_wh.value,
                factories=None,
                warehouses=warehouses,
                customers=customers,
                distance=distance,
                distance_ranges=params.get("distance_ranges", []),
                objective=params.get("objective", "p-median"),
                objective_function=params.get("objective_function", "mindistance"),
                high_service_distance=params.get("high_service_distance", None),
                unit_transport_cost=params.get("unit_transport_cost", 0.1),
                mutually_exclusive=params.get("mutually_exclusive", []),
                plot=plot.value,
                plot_size=params.get("plot_size", (8, 12)),
                hide_inactive=hide_inactive.value,
                force_single_sourcing=params.get("force_single_sourcing", False),
                force_uncapacitated=params.get("force_uncapacitated", False),
                ignore_fixed_cost=params.get("ignore_fixed_cost", False),
                force_open=params.get("force_open"),
                force_closed=params.get("force_closed"),
                force_allocations=params.get("force_allocations"),
                warehouse_marker=params.get("warehouse_marker", "s"),
                warehouse_markercolor=params.get("warehouse_markercolor", "red"),
                warehouse_markersize=int(params.get("warehouse_markersize", 6)),
                customer_marker=params.get("customer_marker", "s"),
                customer_markercolor=params.get("customer_markercolor", "red"),
                customer_markersize=int(params.get("customer_markersize", 6)),
            )
            # print(result)

    button.on_click(run_netopt)

    sec_layout = widgets.Layout(
        border="1px solid #ddd", padding="10px", margin="5px", width="48%"
    )

    # Section 1: General parameters
    sec1 = widgets.VBox(
        [
            widgets.HTML("<h4>Solver parameters</h4>"),
            objective,
            num_wh,
            objective_function,
            high_service_distance,
            distance_ranges,
            force_single_sourcing,
            force_uncapacitated,
            ignore_fixed_cost,
            force_open,
            force_closed,
            force_allocations,
            mutually_exclusive,
            unit_transport_cost,
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
            widgets.HTML("<h4>Plot</h4>"),
            plot,
            hide_inactive,
            plot_size,
            warehouse_marker,
            warehouse_markercolor,
            warehouse_markersize,
            customer_marker,
            customer_markercolor,
            customer_markersize,
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

    # Combine into one HBox
    ui = widgets.HBox([sec1, sec2])

    display(ui, button, output)
