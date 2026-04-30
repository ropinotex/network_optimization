import ipywidgets as widgets
from IPython.display import display, clear_output
from netopt_compat import netopt
from netopt_utils import show_assignments, show_results_summary
# from data_structures import Warehouse, Customer


def parse(txt):
    try:
        return eval(txt) if txt.strip() else None
    except Exception as excp:
        print(f"Error parsing input: {excp}")
        raise excp


class OptimizationResult:
    """Container for optimization results from netopt_ui.

    Usage::

        r = netopt_ui(warehouses, customers)
        # ... click Solve ...
        result = r.result  # dict with solution data
    """

    def __init__(self):
        self._result = None
        self._solved = False

    @property
    def result(self):
        if not self._solved:
            raise ValueError(
                "No solution yet. Click Solve first, then access .result in a new cell."
            )
        return self._result

    def _set(self, value):
        self._result = value
        self._solved = True

    @property
    def is_solved(self):
        return self._solved

    def __repr__(self):
        if self._solved:
            status = (
                self._result.get("status", "Unknown") if self._result else "No solution"
            )
            return f"OptimizationResult(solved=True, status={status})"
        return "OptimizationResult(solved=False — click Solve, then access .result)"


def netopt_ui(warehouses: dict, customers: dict, distance: dict | None = None):
    """User interface for the netopt function.
    Required parameters:
    - warehouses: dict of Warehouse objects
    - customers: dict of Customer objects

    Returns an OptimizationResult container. After clicking Solve,
    access the solution via ``.result`` in a subsequent cell::

        r = netopt_ui(warehouses, customers)
        # ... click Solve ...
        result = r.result

    """

    if not distance:
        try:
            from data_structures import calculate_dm

            print(
                "No distance matrix provided, calculating from coordinates...", end=" "
            )
            distance = calculate_dm(warehouses, customers)
            print("done!")
        except Exception:
            print(
                "No distance matrix provided and failed to calculate it from coordinates."
            )
            distance = None

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
            ("Total cover (min. facilities)", "totalcover"),
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
        description="Coverage radius (km)",
        value=500,
        layout=form_layout,
        style=form_style,
        disabled=True,
    )

    feasibility_warning = widgets.HTML(
        value="",
        layout=widgets.Layout(display="none"),
    )

    capacity_warning = widgets.HTML(
        value="",
        layout=widgets.Layout(display="none"),
    )

    # Cached minimum feasible radius for totalcover (computed once on first need)
    _min_feasible_radius = [None]

    def _get_min_feasible_radius():
        if _min_feasible_radius[0] is not None:
            return _min_feasible_radius[0]
        _dist = distance
        if _dist is None:
            try:
                from data_structures import calculate_dm

                _dist = calculate_dm(warehouses, customers)
            except Exception:
                return None
        warehouses_id = set(warehouses.keys())
        customers_id = set(customers.keys())
        min_r = max(min(_dist[w, c] for w in warehouses_id) for c in customers_id)
        _min_feasible_radius[0] = min_r
        return min_r

    def _update_feasibility_warning(r=None):
        if objective.value != "totalcover":
            feasibility_warning.layout.display = "none"
            return
        if r is None:
            r = high_service_distance.value
        min_r = _get_min_feasible_radius()
        if min_r is None:
            feasibility_warning.layout.display = "none"
            return
        if r < min_r:
            feasibility_warning.value = (
                f'<div style="background:#fff3cd;border:1px solid #ffc107;'
                f'padding:6px 10px;border-radius:4px;color:#856404;margin-top:4px;">'
                f"&#9888; <b>Warning:</b> radius {r:.1f} km is too small &mdash; "
                f"at least one customer cannot reach any facility. "
                f"Minimum feasible radius: <b>{min_r:.1f} km</b>. "
                f"The model will be infeasible."
                f"</div>"
            )
            feasibility_warning.layout.display = ""
        else:
            feasibility_warning.layout.display = "none"

    high_service_distance.observe(
        lambda change: _update_feasibility_warning(change["new"]),
        names="value",
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

    assign_uncovered_to_nearest = widgets.Checkbox(
        description="Assign uncovered to nearest",
        value=False,
        layout=form_layout,
        style=form_style,
        disabled=True,
    )

    ignore_fixed_cost = widgets.Checkbox(
        description="Ignore fixed cost",
        layout=form_layout,
        style=form_style,
    )

    include_unit_handling_cost = widgets.Checkbox(
        description="Include unit handling cost",
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
        value=0.001,
        layout=form_layout,
        style=form_style,
    )

    mutually_exclusive = widgets.Text(
        description="Mutually exclusive",
        placeholder="[(1, 2, 6), (3, 4)]",
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

    # show_assignments_button = widgets.Button(
    #     description="Show assignments",
    #     button_style="warning",
    # )

    output = widgets.Output()
    container = OptimizationResult()

    # Function to update widget states based on objective selection
    def on_objective_change(change):
        new_obj = change["new"]

        # num_wh: only meaningful for p-median and p-cover (totalcover finds minimum automatically)
        num_wh.disabled = new_obj not in ("p-median", "p-cover")

        # objective_function sub-selector: only for p-median
        if new_obj == "p-median":
            objective_function.disabled = False
        else:
            objective_function.disabled = True
            objective_function.value = "mindistance"

        # Coverage/service radius: enabled for p-cover and totalcover
        if new_obj in ("p-cover", "totalcover"):
            high_service_distance.disabled = False
            high_service_distance.description = (
                "Service radius R (km)"
                if new_obj == "p-cover"
                else "Coverage radius R (km)"
            )
        else:
            high_service_distance.disabled = True

        # assign_uncovered_to_nearest: only meaningful for p-cover
        if new_obj == "p-cover":
            assign_uncovered_to_nearest.disabled = False
        else:
            assign_uncovered_to_nearest.value = False
            assign_uncovered_to_nearest.disabled = True

        _update_feasibility_warning()

        # force_uncapacitated and force_single_sourcing:
        # - coverage models are always uncapacitated and single-sourced
        # - FLP variants have fixed values
        # - p-median is user-controlled
        if new_obj in ("p-cover", "totalcover"):
            force_uncapacitated.value = True
            force_uncapacitated.disabled = True
            force_single_sourcing.value = True
            force_single_sourcing.disabled = True
        elif new_obj == "UFLP":
            force_uncapacitated.value = True
            force_uncapacitated.disabled = True
            force_single_sourcing.disabled = False
        elif new_obj == "CFLP":
            force_uncapacitated.value = False
            force_uncapacitated.disabled = True
            force_single_sourcing.disabled = False
            missing = [
                w_id
                for w_id, w in warehouses.items()
                if not getattr(w, "capacity", None)
            ]
            if missing:
                capacity_warning.value = (
                    f'<div style="background:#fff3cd;border:1px solid #ffc107;'
                    f'padding:6px 10px;border-radius:4px;color:#856404;margin-top:4px;">'
                    f"&#9888; <b>Warning:</b> {len(missing)} warehouse(s) have no capacity set: "
                    f"{missing}. They will be <b>excluded</b> from the CFLP model."
                    f"</div>"
                )
                capacity_warning.layout.display = ""
            else:
                capacity_warning.layout.display = "none"
        else:
            force_uncapacitated.disabled = False
            force_single_sourcing.disabled = False
            capacity_warning.layout.display = "none"

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
                    "include_unit_handling_cost": include_unit_handling_cost.value,
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

            obj = params.get("objective", "p-median")

            # Validate coverage/service radius for coverage problems
            if obj in ("p-cover", "totalcover") and not params.get(
                "high_service_distance"
            ):
                print("Error: coverage radius must be > 0 for coverage problems")
                return

            # For CFLP, discard warehouses with no capacity
            active_warehouses = warehouses
            active_distance = distance
            if obj == "CFLP":
                active_warehouses = {
                    w_id: w
                    for w_id, w in warehouses.items()
                    if getattr(w, "capacity", None)
                }
                if distance:
                    active_distance = {
                        k: v for k, v in distance.items() if k[0] in active_warehouses
                    }

            # Build coverage-specific keyword arguments
            coverage_kwargs = {}
            if obj == "p-cover":
                coverage_kwargs["high_service_distance"] = params.get(
                    "high_service_distance"
                )
                coverage_kwargs["assign_uncovered_to_nearest"] = (
                    assign_uncovered_to_nearest.value
                )
            elif obj == "totalcover":
                coverage_kwargs["coverage_distance"] = params.get(
                    "high_service_distance"
                )

            try:
                print("Running optimization...  This may take a moment...")
                # print(
                #     f"Model parameters: {params.get('include_unit_handling_cost', False)=}"
                # )

                result = netopt(
                    num_warehouses=num_wh.value,
                    factories=None,
                    warehouses=active_warehouses,
                    customers=customers,
                    distance=active_distance,
                    distance_ranges=params.get("distance_ranges", []),
                    objective=obj,
                    objective_function=params.get("objective_function", "mindistance"),
                    unit_transport_cost=params.get("unit_transport_cost", 0.1),
                    include_unit_handling_cost=params.get(
                        "include_unit_handling_cost", False
                    ),
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
                    **coverage_kwargs,
                )
            except ValueError as exc:
                from IPython.display import display as _display, HTML as _HTML

                _display(
                    _HTML(
                        f'<div style="background:#f8d7da;border:1px solid #f5c6cb;'
                        f'padding:10px 14px;border-radius:4px;color:#721c24;margin-top:6px;">'
                        f"<b>&#10060; Validation Error:</b> {exc}</div>"
                    )
                )
                return
            if result:
                container._set(result)
                show_results_summary(
                    result,
                    warehouses=active_warehouses,
                    unit_transport_cost=params.get("unit_transport_cost", 0),
                    # include_unit_handling_cost=params.get("include_unit_handling_cost", False),
                )
                show_assignments(result)

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
            feasibility_warning,
            assign_uncovered_to_nearest,
            distance_ranges,
            force_single_sourcing,
            force_uncapacitated,
            capacity_warning,
            ignore_fixed_cost,
            include_unit_handling_cost,
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

    return container


def edit_warehouse_ui(warehouses: dict, warehouse_id: int) -> dict:
    """Edit a warehouse in the warehouses dictionary."""

    warehouse = warehouses.get(warehouse_id, None)
    if not warehouse:
        print(f"Warehouse {warehouse_id} not found.")
        return warehouses

    # Define a consistent layout for all form elements
    form_layout = widgets.Layout(
        width="50%"  # Full width for the widget itself
    )

    # Define a consistent style for all form elements
    form_style = {"description_width": "200px"}  # Fixed width for all descriptions

    warehouse_name = widgets.Text(
        description="Warehouse name",
        value=warehouse.name,
        disabled=True,
        layout=form_layout,
        style=form_style,
    )

    w_id = widgets.IntText(
        description="Warehouse ID",
        value=warehouse_id,
        disabled=True,
        layout=form_layout,
        style=form_style,
    )

    capacity = widgets.Text(
        description="Capacity",
        value=str(warehouse.capacity),
        layout=form_layout,
        style=form_style,
    )

    fixed_cost = widgets.Text(
        description="Fixed cost",
        value=str(warehouse.fixed_cost),
        layout=form_layout,
        style=form_style,
    )

    button = widgets.Button(
        description="Update",
        button_style="success",
    )

    output = widgets.Output()

    # Create a container for all widgets
    container = widgets.VBox(
        [
            widgets.HTML("<h3>Edit Warehouse</h3>"),
            warehouse_name,
            w_id,
            capacity,
            fixed_cost,
            button,
            output,
        ]
    )

    # Display with ID for later clearing
    display_handle = display(container, display_id="edit_warehouse_form")

    # display(warehouse_name, w_id, capacity, fixed_cost, output, button)

    def update_warehouse(_):
        with output:
            clear_output()
            try:
                old_data = warehouses.get(warehouse_id, None)
                from data_structures import Warehouse

                warehouses[warehouse_id] = Warehouse(
                    name=old_data.name,
                    city=old_data.city,
                    state=old_data.state,
                    zipcode=old_data.zipcode,
                    latitude=old_data.latitude,
                    longitude=old_data.longitude,
                    capacity=parse(capacity.value) or old_data.capacity,
                    fixed_cost=parse(fixed_cost.value) or old_data.fixed_cost,
                    unit_handling_cost=getattr(old_data, "unit_handling_cost", 0.0),
                )

                print(f"Warehouse {warehouse_id} updated successfully.")

                # Add a clear button
                close_button = widgets.Button(
                    description="Close form",
                    button_style="info",
                )

                def clear_form(_):
                    # Clear form by replacing it with an empty widget
                    display(widgets.HTML(""), display_id="edit_warehouse_form")

                close_button.on_click(clear_form)
                display(close_button)

                # display(widgets.HTML(""), display_id="edit_warehouse_form")

            except Exception as excp:
                print(f"Error updating warehouse: {excp}")
                raise excp

    button.on_click(update_warehouse)


def add_warehouse_ui(warehouses: dict) -> dict:
    """Add a new warehouse to the warehouses dictionary."""

    # Calculate next available warehouse ID
    next_id = max(warehouses.keys()) + 1 if warehouses else 1

    # Define a consistent layout for all form elements
    form_layout = widgets.Layout(
        width="50%"  # Half width for the widget itself
    )

    # Define a consistent style for all form elements
    form_style = {"description_width": "200px"}  # Fixed width for all descriptions

    warehouse_name = widgets.Text(
        description="Warehouse name",
        placeholder="Insert a unique name (can be the same as city)",
        layout=form_layout,
        style=form_style,
    )

    w_id = widgets.IntText(
        description="Warehouse ID (automatically assigned)",
        value=next_id,
        disabled=True,
        layout=form_layout,
        style=form_style,
    )

    city = widgets.Text(
        description="City",
        placeholder="Insert the city name",
        layout=form_layout,
        style=form_style,
    )

    state = widgets.Text(
        description="State",
        placeholder="Insert the state or country name",
        layout=form_layout,
        style=form_style,
    )

    zipcode = widgets.Text(
        description="Zip code (optional)",
        layout=form_layout,
        style=form_style,
    )

    latitude = widgets.FloatText(
        description="Latitude",
        placeholder="40.7128",
        layout=form_layout,
        style=form_style,
    )

    longitude = widgets.FloatText(
        description="Longitude",
        placeholder="-74.0060",
        layout=form_layout,
        style=form_style,
    )

    capacity = widgets.Text(
        description="Capacity",
        value="0",
        placeholder="Insert the capacity",
        layout=form_layout,
        style=form_style,
    )

    fixed_cost = widgets.Text(
        description="Fixed cost",
        value="0",
        placeholder="Insert the fixed cost",
        layout=form_layout,
        style=form_style,
    )

    unit_handling_cost = widgets.Text(
        description="Unit handling cost",
        value="0",
        placeholder="Insert the unit handling cost",
        layout=form_layout,
        style=form_style,
    )

    use_geocoding = widgets.Checkbox(
        description="Use geocoding to find coordinates",
        value=False,
        layout=form_layout,
        style=form_style,
    )

    button = widgets.Button(
        description="Add Warehouse",
        button_style="success",
    )

    output = widgets.Output()

    # Create a container for all widgets
    container = widgets.VBox(
        [
            widgets.HTML("<h3>Add New Warehouse</h3>"),
            w_id,
            warehouse_name,
            city,
            state,
            zipcode,
            latitude,
            longitude,
            capacity,
            fixed_cost,
            unit_handling_cost,
            use_geocoding,
            button,
            output,
        ]
    )

    # Display with ID for later clearing
    display_handle = display(container, display_id="add_warehouse_form")

    # Function to lookup coordinates if requested
    def lookup_coordinates(city_name, state_name):
        from netopt import get_city_coords

        location = f"{city_name}, {state_name}"
        lat, lon = get_city_coords(location)

        if lat is None or lon is None:
            return None, None
        return lat, lon

    # Update function for geocoding checkbox
    def on_geocoding_change(change):
        if change["new"]:
            latitude.disabled = True
            longitude.disabled = True
        else:
            latitude.disabled = False
            longitude.disabled = False

    use_geocoding.observe(on_geocoding_change, names="value")

    def add_new_warehouse(_):
        with output:
            clear_output()
            try:
                # Validate required fields
                if not warehouse_name.value:
                    print("Error: Warehouse name is required")
                    return

                if not city.value:
                    print("Error: City is required")
                    return

                if not state.value:
                    print("Error: State is required")
                    return

                # Get coordinates either from inputs or geocoding
                lat, lon = None, None
                if use_geocoding.value:
                    print(f"Looking up coordinates for {city.value}, {state.value}...")
                    lat, lon = lookup_coordinates(city.value, state.value)
                    if lat is None or lon is None:
                        print(
                            f"Error: Could not find coordinates for {city.value}, {state.value}"
                        )
                        print("Please enter coordinates manually")
                        return
                    print(f"Found coordinates: {lat}, {lon}")
                else:
                    if latitude.value is None or longitude.value is None:
                        print("Error: Latitude and longitude are required")
                        return
                    lat, lon = latitude.value, longitude.value

                # Create new warehouse
                from data_structures import Warehouse

                new_warehouse = Warehouse(
                    name=warehouse_name.value,
                    city=city.value,
                    state=state.value,
                    zipcode=zipcode.value,
                    latitude=lat,
                    longitude=lon,
                    capacity=parse(capacity.value),
                    fixed_cost=parse(fixed_cost.value) or 0,
                    unit_handling_cost=parse(unit_handling_cost.value) or 0.0,
                )

                # Add to warehouses dictionary
                warehouses[w_id.value] = new_warehouse

                print(
                    f"Warehouse {w_id.value} ({warehouse_name.value}) added successfully."
                )
                print(f"Location: {city.value}, {state.value} ({lat}, {lon})")
                print(f"Capacity: {parse(capacity.value) or 'Unlimited'}")
                print(f"Fixed cost: {parse(fixed_cost.value) or 1000}")
                print(f"Unit handling cost: {parse(unit_handling_cost.value) or 0.0}")

                # Add a clear button
                close_button = widgets.Button(
                    description="Clear Form",
                    button_style="info",
                )

                def clear_form(_):
                    # Clear form by replacing it with an empty widget
                    display(widgets.HTML(""), display_id="add_warehouse_form")

                close_button.on_click(clear_form)
                display(close_button)

            except Exception as excp:
                print(f"Error adding warehouse: {excp}")
                raise excp

    button.on_click(add_new_warehouse)

    # return warehouses


def delete_warehouse_ui(warehouses: dict) -> dict:
    """Delete a warehouse from the warehouses dictionary."""

    # Define a consistent layout for all form elements
    form_layout = widgets.Layout(
        width="50%"  # Half width for the widget itself
    )

    # Define a consistent style for all form elements
    form_style = {"description_width": "200px"}  # Fixed width for all descriptions

    # Create a dropdown with all available warehouses
    warehouse_options = [(f"{w_id}: {w.name}", w_id) for w_id, w in warehouses.items()]

    warehouse_selector = widgets.Dropdown(
        options=warehouse_options,
        description="Select warehouse",
        layout=form_layout,
        style=form_style,
    )

    # Preview area for selected warehouse info
    preview = widgets.Output()

    # Button to confirm deletion
    delete_button = widgets.Button(
        description="Delete Warehouse",
        button_style="danger",  # Red button to indicate destructive action
        disabled=False,
    )

    # Cancel button
    cancel_button = widgets.Button(
        description="Cancel",
        button_style="info",
    )

    # Output area for status messages
    output = widgets.Output()

    # Create a container for all widgets
    container = widgets.VBox(
        [
            widgets.HTML("<h3>Delete Warehouse</h3>"),
            widgets.HTML(
                "<p>Select a warehouse to delete and confirm your selection.</p>"
            ),
            warehouse_selector,
            preview,
            widgets.HBox([delete_button, cancel_button]),
            output,
        ]
    )

    # Display with ID for later clearing
    display_handle = display(container, display_id="delete_warehouse_form")

    # Update preview when selection changes
    def update_preview(change):
        with preview:
            clear_output()
            if change["new"] is None:
                print("No warehouse selected")
                delete_button.disabled = True
                return

            w_id = change["new"]
            warehouse = warehouses.get(w_id)

            if warehouse:
                print(f"ID: {w_id}")
                print(f"Name: {warehouse.name}")
                print(f"Location: {warehouse.city}, {warehouse.state}")
                print(f"Coordinates: ({warehouse.latitude}, {warehouse.longitude})")
                print(f"Capacity: {warehouse.capacity or 'Unlimited'}")
                print(f"Fixed Cost: {warehouse.fixed_cost}")
                delete_button.disabled = False
            else:
                print("Warehouse not found")
                delete_button.disabled = True

    warehouse_selector.observe(update_preview, names="value")

    # Trigger initial preview update
    if warehouse_options:
        with preview:
            w_id = warehouse_selector.value
            warehouse = warehouses.get(w_id)
            if warehouse:
                print(f"ID: {w_id}")
                print(f"Name: {warehouse.name}")
                print(f"Location: {warehouse.city}, {warehouse.state}")
                print(f"Coordinates: ({warehouse.latitude}, {warehouse.longitude})")
                print(f"Capacity: {warehouse.capacity or 'Unlimited'}")
                print(f"Fixed Cost: {warehouse.fixed_cost}")
    else:
        with preview:
            print("No warehouses available")
            delete_button.disabled = True

    # Delete function
    def confirm_delete(_):
        with output:
            clear_output()
            w_id = warehouse_selector.value

            if w_id is None:
                print("No warehouse selected")
                return

            try:
                warehouse = warehouses.get(w_id)
                if warehouse:
                    warehouse_name = warehouse.name
                    # Delete the warehouse
                    del warehouses[w_id]
                    print(f"Warehouse {w_id} ({warehouse_name}) deleted successfully.")

                    # Update the dropdown options
                    new_options = [
                        (f"{w_id}: {w.name}", w_id) for w_id, w in warehouses.items()
                    ]
                    warehouse_selector.options = new_options

                    # Clear the preview
                    with preview:
                        clear_output()
                        if new_options:
                            w_id = warehouse_selector.value
                            warehouse = warehouses.get(w_id)
                            if warehouse:
                                print(f"ID: {w_id}")
                                print(f"Name: {warehouse.name}")
                                print(f"Location: {warehouse.city}, {warehouse.state}")
                                print(
                                    f"Coordinates: ({warehouse.latitude}, {warehouse.longitude})"
                                )
                                print(f"Capacity: {warehouse.capacity or 'Unlimited'}")
                                print(f"Fixed Cost: {warehouse.fixed_cost}")
                        else:
                            print("No warehouses available")
                            delete_button.disabled = True
                else:
                    print(f"Error: Warehouse {w_id} not found")

                # Add a close button
                close_button = widgets.Button(
                    description="Close Form",
                    button_style="info",
                )

                def clear_form(_):
                    # Clear form by replacing it with an empty widget
                    display(widgets.HTML(""), display_id="delete_warehouse_form")

                close_button.on_click(clear_form)
                display(close_button)

            except Exception as excp:
                print(f"Error deleting warehouse: {excp}")
                raise excp

    # Cancel function
    def cancel_delete(_):
        display(widgets.HTML(""), display_id="delete_warehouse_form")

    # Connect button handlers
    delete_button.on_click(confirm_delete)
    cancel_button.on_click(cancel_delete)

    # return warehouses
