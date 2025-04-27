from network_factory import solve_network_optimization


def netopt(
    num_warehouses: int,
    factories: dict | None,
    warehouses: dict,
    customers: dict,
    distance: dict | None = None,
    distance_ranges: list | None = None,
    objective: str = "",
    high_service_distance: float | None = None,
    avg_service_distance: float | None = None,
    max_service_distance: float | None = None,
    force_open: list | None = None,
    force_closed: list | None = None,
    force_single_sourcing: bool = True,
    force_uncapacitated: bool = False,
    force_allocations: list | None = None,
    ignore_fixed_cost: bool = False,
    plot: bool = True,
    plot_size: tuple = (8, 12),
    hide_inactive: bool = False,
    hide_flows: bool = False,
    solver_log: bool = False,
    unit_transport_cost: float = 0.1,
    mutually_exclusive: list | None = None,
    **kwargs,
):
    """
    Backward compatibility wrapper for the netopt function.
    This function forwards all parameters to the new solve_network_optimization function.

    For documentation, see the original netopt function.
    """
    return solve_network_optimization(
        objective=objective,
        warehouses=warehouses,
        customers=customers,
        distance=distance,
        factories=factories,
        num_warehouses=num_warehouses,
        high_service_distance=high_service_distance,
        avg_service_distance=avg_service_distance,
        max_service_distance=max_service_distance,
        force_open=force_open,
        force_closed=force_closed,
        force_single_sourcing=force_single_sourcing,
        force_uncapacitated=force_uncapacitated,
        force_allocations=force_allocations,
        ignore_fixed_cost=ignore_fixed_cost,
        plot=plot,
        plot_size=plot_size,
        hide_inactive=hide_inactive,
        hide_flows=hide_flows,
        solver_log=solver_log,
        unit_transport_cost=unit_transport_cost,
        mutually_exclusive=mutually_exclusive,
        distance_ranges=distance_ranges,
        **kwargs,
    )
