from abc import ABC, abstractmethod
import pulp as pl
import pandas as pd
import matplotlib.pyplot as plt


# Define color codes
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class NetworkOptimizer(ABC):
    """Base class for network optimization models

    This class provides common functionality for different network optimization models
    including p-median, p-cover, uncapacitated FLP, and capacitated FLP.
    """

    def __init__(
        self,
        objective: str,
        warehouses: dict,
        customers: dict,
        distance: dict,
        factories: dict = None,
        distance_ranges: list | None = None,
        force_open: list | None = None,
        force_closed: list | None = None,
        force_single_sourcing: bool = True,
        force_uncapacitated: bool = False,
        force_allocations: list[tuple] | None = None,
        mutually_exclusive: list[tuple[int, int]] | None = None,
        **kwargs,
    ):
        """Initialize the base network optimizer

        Args:
            warehouses: Dictionary of warehouse objects
            customers: Dictionary of customer objects
            distance: Distance matrix between warehouses and customers
            factories: Optional dictionary of factory objects
            distance_ranges: List of distances for calculating demand percentages
            force_open: List of warehouse IDs that must be open
            force_closed: List of warehouse IDs that must be closed
            force_single_sourcing: Whether customers must be served by a single warehouse
            force_uncapacitated: Whether to ignore warehouse capacities
            force_allocations: List of (warehouse_id, customer_id) pairs forcing allocations
            mutually_exclusive: List of warehouse ID pairs that cannot be open simultaneously
        """
        # Store input parameters
        self.objective = objective
        self.warehouses = warehouses
        self.customers = customers
        self.distance = distance
        self.factories = factories if factories else {}
        self.force_open = force_open if force_open else []
        self.force_closed = force_closed if force_closed else []
        self.force_single_sourcing = force_single_sourcing
        self.force_uncapacitated = force_uncapacitated
        self.force_allocations = force_allocations if force_allocations else []
        self.mutually_exclusive = mutually_exclusive if mutually_exclusive else []

        # Set up distance ranges
        if not distance_ranges:
            self.distance_ranges = [0, 99999]
        else:
            self.distance_ranges = distance_ranges
            if self.distance_ranges[0] != 0:
                self.distance_ranges.insert(0, 0)
            if self.distance_ranges[-1] != 99999:
                self.distance_ranges.append(99999)

        # Set IDs for entities
        self.factories_id = set(self.factories.keys()) if self.factories else set([0])
        self.warehouses_id = set(self.warehouses.keys())
        self.customers_id = set(self.customers.keys())

        # Initialize variables for model
        self.model = None
        self.assignment_vars = None
        self.facility_status_vars = None

        # Initialize solution storage
        self.active_warehouses = set()
        self.flows = set()
        self.multi_sourced = {}
        self.solution = None

    def build_model(self, is_maximization: bool = False):
        """Build the base optimization model

        Args:
            is_maximization: Whether the objective is to be maximized
        """
        # Create model
        problem_type = pl.LpMaximize if is_maximization else pl.LpMinimize
        self.model = pl.LpProblem("NetworkOptimizationModel", problem_type)

        # Create decision variables
        self._create_decision_vars()

        # Add common constraints
        self._add_customer_service_constraints()
        self._add_logical_constraints()
        self._add_warehouse_force_constraints()
        self._add_mutual_exclusivity_constraints()
        self._add_allocation_constraints()

        # Specific constraints for each model type and objective function
        if self.objective == "CFLP" or (
            self.objective in ("p-median", "p-cover") and not self.force_uncapacitated
        ):
            # print("Adding capacity constraints...")
            print("- Capacitated model.")
            self._add_capacity_constraints()
        else:
            print("- Uncapacitated model.")

    def _create_decision_vars(self):
        """Create common decision variables for the model"""
        # Create facility status variables
        self.facility_status_vars = pl.LpVariable.dicts(
            name="Open",
            indices=[w for w in self.warehouses_id],
            lowBound=0,
            upBound=1,
            cat=pl.LpInteger,
        )

        # Create assignment variables
        if self.force_single_sourcing:
            print("- Single sourcing model.")  # using integer variables for assignment
            self.assignment_vars = pl.LpVariable.dicts(
                name="Flow",
                indices=[(w, c) for w in self.warehouses_id for c in self.customers_id],
                lowBound=0,
                upBound=1,
                cat=pl.LpInteger,
            )
        else:
            print(
                "- Multi-sourcing model."
            )  # using continuous variables for assignment
            self.assignment_vars = pl.LpVariable.dicts(
                name="Flow",
                indices=[(w, c) for w in self.warehouses_id for c in self.customers_id],
                lowBound=0.0,
                upBound=1.0,
                cat=pl.LpContinuous,
            )

    def _add_customer_service_constraints(self):
        """Add constraints ensuring each customer is fully served
        Used in all optimization models"""
        for c in self.customers_id:
            self.model += pl.LpConstraint(
                e=pl.lpSum([self.assignment_vars[w, c] for w in self.warehouses_id]),
                sense=pl.LpConstraintEQ,
                rhs=1,
                name=f"Customer_{c}_served",
            )

    def _add_logical_constraints(self):
        """Add logical constraints linking assignment and facility variables
        Used in all optimization models"""
        for w in self.warehouses_id:
            for c in self.customers_id:
                self.model += pl.LpConstraint(
                    e=self.assignment_vars[w, c] - self.facility_status_vars[w],
                    sense=pl.LpConstraintLE,
                    rhs=0,
                    name=f"Logical_constraint_between_customer_{c}_and_warehouse_{w}",
                )

    def _add_capacity_constraints(self):
        """Add capacity constraints for warehouses"""
        for w_id, w in self.warehouses.items():
            if hasattr(w, "capacity") and w.capacity:
                self.model += pl.LpConstraint(
                    e=pl.lpSum(
                        [
                            self.customers[c].demand * self.assignment_vars[w_id, c]
                            for c in self.customers_id
                        ]
                    ),
                    sense=pl.LpConstraintLE,
                    rhs=w.capacity,
                    name=f"Capacity_limit_warehouse_{w_id}",
                )

    def _add_warehouse_force_constraints(self):
        """Add constraints for forcing warehouses open or closed
        Used in all optimization models"""

        # Force open warehouses
        for w in self.force_open:
            try:
                self.facility_status_vars[w].lowBound = 1
            except KeyError:
                print(f"Warehouse {w} does not exist")

        # Force closed warehouses
        for w in self.force_closed:
            try:
                self.facility_status_vars[w].upBound = 0
            except KeyError:
                print(f"Warehouse {w} does not exist")

    def _add_mutual_exclusivity_constraints(self):
        """Add constraints for mutually exclusive warehouses
        Used in all optimization models"""

        if self.mutually_exclusive:
            for seq in self.mutually_exclusive:
                self.model += pl.LpConstraint(
                    e=pl.lpSum([self.facility_status_vars[w] for w in seq]),
                    sense=pl.LpConstraintLE,
                    rhs=1,
                    name=f"Mutually_exclusive_warehouses_{seq}",
                )

    def _add_allocation_constraints(self):
        """Add constraints for forced allocations
        Used in all optimization models"""
        if self.force_allocations:
            try:
                for each in self.force_allocations:
                    self.assignment_vars[each[0], each[1]].lowBound = 1
                    self.assignment_vars[each[0], each[1]].upBound = 1
            except KeyError:
                pass

    @abstractmethod
    def set_objective(self):
        """Set the objective function for the model - must be implemented by subclasses"""
        pass

    def solve(self, solver_log=False, time_limit=120):
        """Solve the optimization model

        Args:
            solver_log: Whether to display solver log
            time_limit: Time limit for solving in seconds

        Returns:
            Solution dictionary or None if infeasible
        """
        print()
        print("SOLVING (time limit = 120 seconds)...", end="")
        _solver = pl.PULP_CBC_CMD(
            keepFiles=False, gapRel=0.00, timeLimit=time_limit, msg=solver_log
        )
        self.model.solve(solver=_solver)
        print("OK")

        if pl.LpStatus[self.model.status] == "Optimal":
            print(
                f"==> Optimization Status: {Colors.GREEN}{Colors.BOLD}{pl.LpStatus[self.model.status]} {Colors.RESET}<==",
            )
        elif pl.LpStatus[self.model.status] == "Infeasible":
            print(
                f"{Colors.RED}{Colors.BOLD}********* ERROR: Model not feasible, don't use the results. ********* {Colors.RESET}"
            )
            return None
        elif pl.LpStatus[self.model.status] == "Not Solved":
            print(
                f"{Colors.RED}{Colors.BOLD}********* ERROR: Model not solved, time limit probably exceeded. ********* {Colors.RESET}"
            )
            return None

        # Extract solution
        self._extract_solution()
        self._analyze_solution()

        return self.solution

    def _extract_solution(self):
        """Extract solution data from the solved model"""
        self.flows = {
            (w, c)
            for w in self.warehouses_id
            for c in self.customers_id
            if self.assignment_vars[w, c].varValue > 0
        }

        self.active_warehouses = {
            w for w in self.warehouses_id if self.facility_status_vars[w].varValue == 1
        }

        # Identify multi-sourced customers
        self.multi_sourced = {}
        for c in self.customers_id:
            suppliers = sum(
                [
                    1 if self.assignment_vars[w, c].varValue > 0 else 0
                    for w in self.warehouses_id
                ]
            )
            if suppliers > 1:
                self.multi_sourced[c] = suppliers

    def _analyze_solution(self):
        """Analyze the solution and create results dictionary"""
        customers_assignment = []
        for w, c in self.flows:
            cust = {
                "Warehouse": str(self.warehouses[w].city),
                "Warehouse_id": w,
                "Customer": str(self.customers[c].city),
                "Customer_id": c,
                "Customer Demand": self.customers[c].demand,
                "Distance": self.distance[w, c],
                "Warehouse Latitude": self.warehouses[w].latitude,
                "Warehouse Longitude": self.warehouses[w].longitude,
                "Customers Latitude": self.customers[c].latitude,
                "Customers Longitude": self.customers[c].longitude,
            }
            customers_assignment.append(cust)

        df_cu = pd.DataFrame.from_records(customers_assignment)

        if not df_cu.empty:
            df_cu = df_cu[["Warehouse", "Customer", "Distance", "Customer Demand"]]
            labels = list(range(1, len(self.distance_ranges)))
            df_cu["distance_range"] = pd.cut(
                df_cu["Distance"],
                bins=self.distance_ranges,
                labels=labels,
                include_lowest=True,
            )

            total_demand = sum(df_cu["Customer Demand"])
            demand_perc_by_ranges = {}
            for band in labels:
                perc_of_demand_in_band = (
                    sum(df_cu[df_cu["distance_range"] == band]["Customer Demand"])
                    / total_demand
                )
                distance_range_lower_limit = self.distance_ranges[band - 1]
                distance_range_upper_limit = self.distance_ranges[band]
                demand_perc_by_ranges[
                    (distance_range_lower_limit, distance_range_upper_limit)
                ] = perc_of_demand_in_band

            df_cu["Weighted_Distance"] = df_cu["Distance"] * df_cu["Customer Demand"]
            avg_weighted_distance = (
                df_cu["Weighted_Distance"].sum() / df_cu["Customer Demand"].sum()
            )

            self.solution = {
                "status": pl.LpStatus[self.model.status],
                "objective_value": pl.value(self.model.objective),
                "avg_weighted_distance": avg_weighted_distance,
                "active_warehouses_id": self.active_warehouses,
                "active_warehouses_name": [
                    self.warehouses[w].name for w in self.active_warehouses
                ],
                "most_distant_customer": df_cu["Distance"].max(),
                "demand_perc_by_ranges": demand_perc_by_ranges,
                "avg_customer_distance": df_cu["Distance"].mean(),
                "multi_sourced_customers": list(self.multi_sourced.keys()),
                "customers_assignment": customers_assignment,
            }
        else:
            self.solution = {
                "status": pl.LpStatus[self.model.status],
                "objective_value": pl.value(self.model.objective),
                "active_warehouses_id": self.active_warehouses,
                "active_warehouses_name": [
                    self.warehouses[w].name for w in self.active_warehouses
                ],
                "multi_sourced_customers": list(self.multi_sourced.keys()),
            }

    def plot_solution(
        self, hide_inactive=False, hide_flows=False, plot_size=(8, 12), **kwargs
    ):
        """Plot the solution using matplotlib

        Args:
            hide_inactive: Whether to hide inactive warehouses
            hide_flows: Whether to hide flows
            plot_size: Size of the plot as a tuple (width, height)
        """

        from netopt import plot_map

        plot_map(
            warehouses=self.warehouses,
            customers=self.customers,
            flows=self.flows,
            active_warehouses=self.active_warehouses,
            hide_inactive=hide_inactive,
            multi_sourced=self.multi_sourced,
            hide_flows=hide_flows,
            plot_size=plot_size,
            options=self._get_plot_options(),
            **kwargs,
        )

    def _get_plot_options(self):
        """Get options for plotting, to be overridden by subclasses"""
        return {}

    def print_solution_details(self):
        """Print detailed information about the solution"""
        print("=" * 40)
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return

        # Print open warehouses
        print(
            f"Open warehouses: ({len(self.active_warehouses)} out of {len(self.warehouses)})"
        )
        total_outflow = 0.0
        for w in self.active_warehouses:
            try:
                outflow = sum(
                    [
                        self.customers[c].demand * self.assignment_vars[w, c].varValue
                        for c in self.customers_id
                    ]
                )
            except TypeError:
                outflow = 0

            total_outflow += outflow

            try:
                assigned_customers = int(
                    sum(
                        [
                            1 if self.assignment_vars[w, c].varValue > 0.0 else 0
                            for c in self.customers_id
                        ]
                    )
                )
            except TypeError:
                assigned_customers = 0

            print(
                f"ID: {w:3} City: {self.warehouses[w].city:20} State: {self.warehouses[w].state:6} "
                f"Num. customers: {assigned_customers:3}  Outflow: {outflow:11.0f} units"
            )

        print(f"\nTotal outflow: {total_outflow:.0f} units")

        # Check capacity utilization
        print("\nWarehouse capacity utilization:")
        for w in self.active_warehouses:
            if hasattr(self.warehouses[w], "capacity") and self.warehouses[w].capacity:
                usage = sum(
                    [
                        self.customers[c].demand * self.assignment_vars[w, c].varValue
                        for c in self.customers_id
                    ]
                )
                utilization = (usage / self.warehouses[w].capacity) * 100
                print(
                    f"Warehouse {w}: {round(utilization, 1)}% ({int(usage)}/{self.warehouses[w].capacity})"
                )

        # Print demand percentages by distance range
        if "demand_perc_by_ranges" in self.solution:
            print("\nDemand coverage by distance:")
            for (lower, upper), percentage in self.solution[
                "demand_perc_by_ranges"
            ].items():
                print(
                    f"% of demand in range {lower:5} - {upper:5}: {round(percentage * 100, 1):4}%"
                )

        # Print distance statistics
        if "most_distant_customer" in self.solution:
            print(
                f"\nMost distant customer is at {self.solution['most_distant_customer']:.1f} km"
            )
            print(
                f"Average customers distance (no weights): {self.solution['avg_customer_distance']:.1f} km"
            )
            print(
                f"Average weighted distance: {self.solution['avg_weighted_distance']:.1f} km"
            )

        # Print multi-sourced customers
        if self.multi_sourced:
            print("\nCustomers served by more than one warehouse")
            for k, v in self.multi_sourced.items():
                print(f"- Customer {k} is served by {v} warehouses")


class PMedianOptimizer(NetworkOptimizer):
    """P-Median optimization model

    Locates p warehouses to minimize the average weighted distance between warehouses and customers.
    """

    def __init__(
        self,
        objective: str,
        objective_function: str,
        num_warehouses: int,
        warehouses: dict,
        customers: dict,
        distance: dict,
        force_uncapacitated: bool = False,
        force_single_sourcing: bool = True,
        unit_transport_cost: float = 0.1,
        ignore_fixed_cost: bool = True,
        **kwargs,
    ):
        """Initialize P-Median optimizer

        Args:
            num_warehouses: Number of warehouses to open (p)
            warehouses: Dictionary of warehouse objects
            customers: Dictionary of customer objects
            distance: Distance matrix
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(
            objective=objective,
            warehouses=warehouses,
            customers=customers,
            distance=distance,
            force_uncapacitated=force_uncapacitated,
            force_single_sourcing=force_single_sourcing,
            **kwargs,
        )
        self.num_warehouses = num_warehouses
        self.objective_function = objective_function  # The objective_function is used only with the p-median model
        self.unit_transport_cost = (
            unit_transport_cost  # Default transport cost per unit per distance
        )
        self.ignore_fixed_cost = ignore_fixed_cost

    def build_model(self, is_maximization: bool = False):
        """Build the P-Median optimization model

        Args:
            is_maximization: Whether the objective is to be maximized (ignored as p-median is always minimization)
        """
        # Build base model (with minimize objective)
        super().build_model(is_maximization=False)

        # Add P-Median specific constraint (exactly p warehouses)
        self.model += pl.LpConstraint(
            e=pl.lpSum([self.facility_status_vars[w] for w in self.warehouses_id]),
            sense=pl.LpConstraintEQ,
            rhs=self.num_warehouses,
            name="Num_of_active_warehouses",
        )

        # Set objective function
        self.set_objective()

    def set_objective(self):
        """Set the P-Median objective function"""
        if self.objective_function == "mindistance":
            print("- Objective function: minimize distance")
            # Minimize total weighted distance
            obj_func = pl.lpSum(
                [
                    self.customers[c].demand
                    * self.distance[w, c]
                    * self.assignment_vars[w, c]
                    for w in self.warehouses_id
                    for c in self.customers_id
                ]
            ) / pl.lpSum([self.customers[c].demand for c in self.customers_id])
        elif self.objective_function == "mincost":
            print("- Objective function: minimize total cost")
            # Minimize total cost (fixed + transportation)
            obj_func = pl.lpSum(
                [
                    self.customers[c].demand
                    * self.distance[w, c]
                    * self.assignment_vars[w, c]
                    * self.unit_transport_cost
                    for w in self.warehouses_id
                    for c in self.customers_id
                ]
            )
            if not self.ignore_fixed_cost:
                # Include fixed costs if not explicitly ignored
                print("- Include warehouses' fixed costs")
                obj_func += pl.lpSum(
                    [
                        self.warehouses[w].fixed_cost * self.facility_status_vars[w]
                        for w in self.warehouses_id
                    ]
                )
            else:
                print("- Ignore warehouses' fixed costs")
        else:
            raise ValueError(
                f"Unknown objective function: {self.objective_function}. Must be 'mindistance' or 'mincost'."
            )
        # print(obj_func)
        self.model.setObjective(obj_func)

    def print_solution_details(self):
        """Print P-Median specific solution details"""
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return
        print("=" * 40)
        print("P-Median optimization results:")
        if self.objective_function == "mindistance":
            print(
                f"Average weighted distance: {int(self.solution['objective_value'])} km"
            )
        elif self.objective_function == "mincost":
            if self.ignore_fixed_cost:
                print(
                    f"Minimum total cost (transportation only): {int(self.solution['objective_value'])}"
                )
            else:
                print(
                    f"Minimum total cost (fixed + transportation): {int(self.solution['objective_value'])}"
                )

        # Print common solution details
        super().print_solution_details()


class PCoverOptimizer(NetworkOptimizer):
    """P-Cover optimization model

    Locates p warehouses to maximize the demand covered within a specified service distance.
    """

    def __init__(
        self,
        objective: str,
        num_warehouses: int,
        warehouses: dict,
        customers: dict,
        distance: dict,
        high_service_distance: float,
        avg_service_distance: float = None,
        max_service_distance: float = None,
        force_uncapacitated: bool = False,
        **kwargs,
    ):
        """Initialize P-Cover optimizer

        Args:
            num_warehouses: Number of warehouses to open (p)
            warehouses: Dictionary of warehouse objects
            customers: Dictionary of customer objects
            distance: Distance matrix
            high_service_distance: Distance within which demand is considered covered
            avg_service_distance: Optional limit on average service distance
            max_service_distance: Optional maximum service distance allowed
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(
            objective=objective,
            warehouses=warehouses,
            customers=customers,
            distance=distance,
            force_uncapacitated=force_uncapacitated,
            **kwargs,
        )
        self.num_warehouses = num_warehouses
        self.high_service_distance = high_service_distance
        self.avg_service_distance = avg_service_distance
        self.max_service_distance = (
            max_service_distance if max_service_distance else 99999
        )

        # Calculate service distance parameters
        self.high_service_dist_par = {
            (w, c): 1 if self.distance[w, c] <= self.high_service_distance else 0
            for w in self.warehouses_id
            for c in self.customers_id
        }

        self.max_service_dist_par = {
            (w, c): 1 if self.distance[w, c] <= self.max_service_distance else 0
            for w in self.warehouses_id
            for c in self.customers_id
        }

    def build_model(self, is_maximization: bool = False):
        """Build the P-Cover optimization model

        Args:
            is_maximization: Whether the objective is to be maximized (ignored as p-cover always uses maximization)
        """
        # Build base model (with maximize objective)
        super().build_model(is_maximization=True)

        # Add P-Cover specific constraint (exactly p warehouses)
        self.model += pl.LpConstraint(
            e=pl.lpSum([self.facility_status_vars[w] for w in self.warehouses_id]),
            sense=pl.LpConstraintEQ,
            rhs=self.num_warehouses,
            name="Num_of_active_warehouses",
        )

        # Add max service distance constraint
        for w in self.warehouses_id:
            for c in self.customers_id:
                self.assignment_vars[w, c].upBound = self.max_service_dist_par[w, c]

        # Add avg service distance constraint if specified
        if self.avg_service_distance:
            self.model += pl.LpConstraint(
                e=pl.lpSum(
                    [
                        self.distance[w, c]
                        * self.customers[c].demand
                        * self.assignment_vars[w, c]
                        for w in self.warehouses_id
                        for c in self.customers_id
                    ]
                )
                / pl.lpSum([self.customers[c].demand for c in self.customers_id]),
                sense=pl.LpConstraintLE,
                rhs=self.avg_service_distance,
                name="Avoid_random_allocations",
            )

        # Set objective function
        self.set_objective()

    def set_objective(self):
        """Set the P-Cover objective function"""
        # Maximize covered demand within high service distance
        total_covered_demand_high_service = pl.lpSum(
            [
                self.customers[c].demand
                * self.high_service_dist_par[w, c]
                * self.assignment_vars[w, c]
                for w in self.warehouses_id
                for c in self.customers_id
            ]
        ) / pl.lpSum([self.customers[c].demand for c in self.customers_id])

        self.model.setObjective(total_covered_demand_high_service)

    def _get_plot_options(self):
        """Get options for plotting P-Cover model"""
        return {"radius": self.high_service_distance}

    def print_solution_details(self):
        """Print P-Cover specific solution details"""
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return

        print(f"P-Cover optimization results:")
        print(
            f"% covered demand within {self.high_service_distance} distance: "
            f"{round(self.solution['objective_value'] * 100, 1)}%"
        )

        # Print common solution details
        super().print_solution_details()


class UncapacitatedFLPOptimizer(NetworkOptimizer):
    """Uncapacitated Facility Location Problem optimizer

    Determines warehouse locations to minimize total cost (fixed + transportation)
    without capacity constraints.
    """

    def __init__(
        self,
        objective: str,
        warehouses: dict,
        customers: dict,
        distance: dict,
        unit_transport_cost: float = 0.1,
        ignore_fixed_cost: bool = False,
        force_single_sourcing: bool = True,
        **kwargs,
    ):
        """Initialize Uncapacitated FLP optimizer

        Args:
            warehouses: Dictionary of warehouse objects
            customers: Dictionary of customer objects
            distance: Distance matrix
            unit_transport_cost: Cost per unit per distance
            ignore_fixed_cost: Whether to ignore fixed costs in optimization
            **kwargs: Additional arguments passed to parent class
        """
        # Force uncapacitated model
        kwargs["force_uncapacitated"] = True
        super().__init__(
            objective=objective,
            warehouses=warehouses,
            customers=customers,
            distance=distance,
            force_single_sourcing=force_single_sourcing,
            **kwargs,
        )
        self.unit_transport_cost = unit_transport_cost
        self.ignore_fixed_cost = ignore_fixed_cost

    def build_model(self, is_maximization: bool = False):
        """Build the Uncapacitated FLP optimization model

        Args:
            is_maximization: Whether the objective is to be maximized (ignored as FLP always uses minimization)
        """
        # Build base model (with minimize objective)
        super().build_model(is_maximization=False)

        # Set objective function
        self.set_objective()

    def set_objective(self):
        """Set the Uncapacitated FLP objective function"""
        # Transportation cost
        total_cost = pl.lpSum(
            [
                self.unit_transport_cost
                * self.customers[c].demand
                * self.distance[w, c]
                * self.assignment_vars[w, c]
                for w in self.warehouses_id
                for c in self.customers_id
            ]
        )

        # Add fixed cost if not ignored
        if not self.ignore_fixed_cost:
            total_cost += pl.lpSum(
                [
                    self.warehouses[w].fixed_cost * self.facility_status_vars[w]
                    for w in self.warehouses_id
                ]
            )

        self.model.setObjective(total_cost)

    def print_solution_details(self):
        """Print Uncapacitated FLP specific solution details"""
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return

        print("Uncapacitated FLP optimization results:")
        print(f"Total cost: {round(self.solution['objective_value'], 0)}")

        # Calculate and print cost breakdown
        transport_cost = sum(
            [
                self.unit_transport_cost
                * self.customers[c].demand
                * self.distance[w, c]
                * self.assignment_vars[w, c].varValue
                for w in self.warehouses_id
                for c in self.customers_id
            ]
        )
        print(f"- Transportation cost: {round(transport_cost, 0)}")

        if not self.ignore_fixed_cost:
            fixed_cost = sum(
                [
                    self.warehouses[w].fixed_cost
                    * self.facility_status_vars[w].varValue
                    for w in self.warehouses_id
                ]
            )
            print(f"- Yearly fixed cost: {round(fixed_cost, 0)}")
        else:
            print("Forced ignoring fixed cost")

        # Print common solution details
        super().print_solution_details()


class CapacitatedFLPOptimizer(UncapacitatedFLPOptimizer):
    """Capacitated Facility Location Problem optimizer

    Determines warehouse locations to minimize total cost (fixed + transportation)
    with capacity constraints.
    """

    def __init__(
        self,
        objective: str,
        warehouses: dict,
        customers: dict,
        distance: dict,
        unit_transport_cost: float = 0.1,
        ignore_fixed_cost: bool = False,
        force_single_sourcing: bool = True,
        **kwargs,
    ):
        """Initialize Capacitated FLP optimizer

        Args:
            warehouses: Dictionary of warehouse objects
            customers: Dictionary of customer objects
            distance: Distance matrix
            unit_transport_cost: Cost per unit per distance
            ignore_fixed_cost: Whether to ignore fixed costs in optimization
            **kwargs: Additional arguments passed to parent class
        """
        # Make sure force_uncapacitated is False for capacitated model
        kwargs.pop("force_uncapacitated", None)
        super().__init__(
            objective=objective,
            warehouses=warehouses,
            customers=customers,
            distance=distance,
            unit_transport_cost=unit_transport_cost,
            ignore_fixed_cost=ignore_fixed_cost,
            force_single_sourcing=force_single_sourcing,
            **kwargs,
        )

    def print_solution_details(self):
        """Print Capacitated FLP specific solution details"""
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return

        print("Capacitated FLP optimization results:")
        print(f"Total cost: {round(self.solution['objective_value'], 0)}")

        # Calculate and print cost breakdown
        transport_cost = sum(
            [
                self.unit_transport_cost
                * self.customers[c].demand
                * self.distance[w, c]
                * self.assignment_vars[w, c].varValue
                for w in self.warehouses_id
                for c in self.customers_id
            ]
        )
        print(f"- Transportation cost: {round(transport_cost, 0)}")

        if not self.ignore_fixed_cost:
            fixed_cost = sum(
                [
                    self.warehouses[w].fixed_cost
                    * self.facility_status_vars[w].varValue
                    for w in self.warehouses_id
                ]
            )
            print(f"- Yearly fixed cost: {round(fixed_cost, 0)}")
        else:
            print("Forced ignoring fixed cost")

        # Check capacity utilization
        # print("\nWarehouse capacity utilization:")
        # for w in self.active_warehouses:
        #     if hasattr(self.warehouses[w], "capacity") and self.warehouses[w].capacity:
        #         usage = sum(
        #             [
        #                 self.customers[c].demand * self.assignment_vars[w, c].varValue
        #                 for c in self.customers_id
        #             ]
        #         )
        #         utilization = (usage / self.warehouses[w].capacity) * 100
        #         print(
        #             f"Warehouse {w}: {round(utilization, 1)}% ({int(usage)}/{self.warehouses[w].capacity})"
        #         )

        # Print common solution details from NetworkOptimizer (skip UncapacitatedFLP)
        NetworkOptimizer.print_solution_details(self)
