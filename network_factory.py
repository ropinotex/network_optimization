from data_structures import calculate_dm
from network_optimizer import (
    NetworkOptimizer,
    PMedianOptimizer,
    PCoverOptimizer,
    UncapacitatedFLPOptimizer,
    CapacitatedFLPOptimizer,
)


def create_network_optimizer(
    objective: str,
    objective_function: str,  # only for p-median
    warehouses: dict,
    customers: dict,
    distance: dict | None = None,
    factories: dict | None = None,
    num_warehouses: int = 0,
    high_service_distance: float = 0,
    avg_service_distance: float = 0,
    max_service_distance: float = 0,
    force_open: list = None,
    force_closed: list = None,
    force_single_sourcing: bool = True,
    force_uncapacitated: bool = False,
    force_allocations: list = None,
    ignore_fixed_cost: bool = False,
    unit_transport_cost: float = 0.1,
    distance_ranges: list = None,
    mutually_exclusive: list = None,
    **kwargs,
) -> NetworkOptimizer:
    """
    Factory function to create the appropriate network optimizer based on the objective.

    Args:
        objective: The objective function type ('mindistance', 'maxcover', 'mincost')
        warehouses: Dictionary of warehouse objects
        customers: Dictionary of customer objects
        distance: Distance matrix between warehouses and customers
        factories: Optional dictionary of factory objects
        num_warehouses: Number of warehouses to open (p) for p-median and p-cover models
        high_service_distance: Distance within which demand is considered covered (for p-cover)
        avg_service_distance: Optional limit on average service distance
        max_service_distance: Optional maximum service distance allowed
        force_open: List of warehouse IDs that must be open
        force_closed: List of warehouse IDs that must be closed
        force_single_sourcing: Whether customers must be served by a single warehouse
        force_uncapacitated: Whether to ignore warehouse capacities
        force_allocations: List of (warehouse_id, customer_id) pairs forcing allocations
        ignore_fixed_cost: Whether to ignore fixed costs in optimization (for FLP)
        unit_transport_cost: Cost per unit per distance (for FLP)
        distance_ranges: List of distances for calculating demand percentages
        mutually_exclusive: List of warehouse ID pairs that cannot be open simultaneously

    Returns:
        An instance of a NetworkOptimizer subclass based on the specified objective
    """

    # Compute distance matrix if not provided
    if not distance and warehouses and customers:
        # Calculate the distance matrix if not provided
        print("Calculating distance matrix...")
        distance = calculate_dm(warehouses, customers)

    # Common parameters for all optimizers
    common_params = {
        "factories": factories,
        "warehouses": warehouses,
        "customers": customers,
        "distance": distance,
        "force_open": force_open,
        "force_closed": force_closed,
        "force_allocations": force_allocations,
        "mutually_exclusive": mutually_exclusive,
        "distance_ranges": distance_ranges,
    }
    # print("=====> KWARGS <=====")
    # print(kwargs)
    # print("=====> COMMON PARAMS <=====")
    # print(common_params)

    # Create the appropriate optimizer based on objective
    if objective == "p-median":
        if not num_warehouses:
            raise ValueError(
                "num_warehouses must be specified for p-median optimization"
            )

        print("Creating p-median optimizer...")
        print("Model's characteristics:")
        optimizer = PMedianOptimizer(
            objective=objective,
            objective_function=objective_function,
            num_warehouses=num_warehouses,
            ignore_fixed_cost=ignore_fixed_cost,
            unit_transport_cost=unit_transport_cost,
            force_uncapacitated=force_uncapacitated,
            force_single_sourcing=force_single_sourcing,
            **common_params,
            **kwargs,
        )

    elif objective == "p-cover":
        if not num_warehouses:
            raise ValueError(
                "num_warehouses must be specified for p-cover optimization"
            )
        if not high_service_distance:
            raise ValueError(
                "high_service_distance must be specified for p-cover optimization"
            )

        print("Creating p-cover optimizer...")
        optimizer = PCoverOptimizer(
            objective=objective,
            num_warehouses=num_warehouses,
            high_service_distance=high_service_distance,
            avg_service_distance=avg_service_distance,
            max_service_distance=max_service_distance,
            ignore_fixed_cost=ignore_fixed_cost,
            force_uncapacitated=force_uncapacitated,
            **common_params,
            **kwargs,
        )

    elif objective == "UFLP":
        print("Creating uncapacitated FLP optimizer...")
        optimizer = UncapacitatedFLPOptimizer(
            objective=objective,
            unit_transport_cost=unit_transport_cost,
            ignore_fixed_cost=ignore_fixed_cost,
            force_single_sourcing=force_single_sourcing,
            **common_params,
            **kwargs,
        )

    elif objective == "CFLP":
        print("Creating capacitated FLP optimizer...")
        optimizer = CapacitatedFLPOptimizer(
            objective=objective,
            unit_transport_cost=unit_transport_cost,
            ignore_fixed_cost=ignore_fixed_cost,
            force_single_sourcing=force_single_sourcing,
            **common_params,
            **kwargs,
        )

    else:
        raise ValueError(
            f"Unknown objective: {objective}. Must be one of: 'p-median', 'p-cover', 'UFLP', 'CFLP'."
        )

    return optimizer


def solve_network_optimization(
    objective: str,
    warehouses: dict,
    customers: dict,
    distance: dict | None = None,
    **kwargs,
) -> dict:
    """
    Convenience function to create an optimizer, solve the model and return results

    Args:
        objective: The objective function type ('mindistance', 'maxcover', 'mincost')
        warehouses: Dictionary of warehouse objects
        customers: Dictionary of customer objects
        distance: Distance matrix between warehouses and customers
        **kwargs: Additional parameters for create_network_optimizer

    Returns:
        Solution dictionary with optimization results or None if infeasible
    """
    # Extract plotting parameters
    plot = kwargs.pop("plot", False)
    hide_inactive = kwargs.pop("hide_inactive", False)
    hide_flows = kwargs.pop("hide_flows", False)
    plot_size = kwargs.pop("plot_size", (8, 12))
    solver_log = kwargs.pop("solver_log", False)

    # Create and build the model
    optimizer = create_network_optimizer(
        objective=objective,
        warehouses=warehouses,
        customers=customers,
        distance=distance,
        **kwargs,
    )

    # Build the optimization model
    optimizer.build_model()

    # if kwargs.get("print_model", False):
    #     print(optimizer.model)

    # Solve the model
    solution = optimizer.solve(solver_log=solver_log)

    # If requested, print detailed solution and plot
    if solution:
        optimizer.print_solution_details()

        if plot:
            optimizer.plot_solution(
                hide_inactive=hide_inactive,
                hide_flows=hide_flows,
                plot_size=plot_size,
                **kwargs,
            )

    return solution
