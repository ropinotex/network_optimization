from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pulp as pl
import pandas as pd

from data_structures import calculate_dm


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


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass
class ValidationIssue:
    severity: Severity
    code: str  # machine-readable tag, e.g. "FORCE_OPEN_CLOSED_CONFLICT"
    message: str  # human-readable explanation

    def __str__(self):
        return f"[{self.severity.value}] {self.message}"


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
        distance: dict | None = None,
        factories: dict | None = None,
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
        if distance:
            self.distance = distance
        else:
            print("Calculating distance matrix...")
            self.distance = calculate_dm(self.warehouses, self.customers)

        self.factories = factories if factories else {}
        self.force_open = force_open if force_open else []
        self.force_closed = force_closed if force_closed else []
        self.force_single_sourcing = force_single_sourcing
        self.force_uncapacitated = force_uncapacitated
        self.force_allocations = force_allocations if force_allocations else []
        self.mutually_exclusive = mutually_exclusive if mutually_exclusive else []

        self.gapRel = kwargs.get("gapRel", 0.0)  # Default gap tolerance
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

    def validate(self) -> list[ValidationIssue]:
        """Run pre-solve feasibility checks. Returns a list of ValidationIssue objects.
        Subclasses should call super().validate() and extend the returned list."""
        issues: list[ValidationIssue] = []

        # force_open / force_closed intersection
        conflict = set(self.force_open) & set(self.force_closed)
        if conflict:
            issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "FORCE_OPEN_CLOSED_CONFLICT",
                    f"Warehouses {sorted(conflict)} appear in both force_open and force_closed. "
                    f"A warehouse cannot be simultaneously forced open and closed.",
                )
            )

        # mutually_exclusive group with >= 2 force_open members
        force_open_set = set(self.force_open)
        for group in self.mutually_exclusive:
            overlap = force_open_set & set(group)
            if len(overlap) >= 2:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "MUTUALLY_EXCLUSIVE_FORCE_OPEN",
                        f"Mutually exclusive group {list(group)} has {len(overlap)} members also "
                        f"in force_open: {sorted(overlap)}. At most 1 can be open simultaneously.",
                    )
                )

        # force_allocations: unknown IDs or closed warehouse
        for w_id, c_id in self.force_allocations:
            if w_id not in self.warehouses_id:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "FORCE_ALLOC_UNKNOWN_WAREHOUSE",
                        f"force_allocations references warehouse ID {w_id} which does not exist.",
                    )
                )
            if c_id not in self.customers_id:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "FORCE_ALLOC_UNKNOWN_CUSTOMER",
                        f"force_allocations references customer ID {c_id} which does not exist.",
                    )
                )
            if w_id in self.force_closed:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "FORCE_ALLOC_CLOSED_WAREHOUSE",
                        f"force_allocations requires warehouse {w_id} to serve customer {c_id}, "
                        f"but warehouse {w_id} is in force_closed.",
                    )
                )

        # customers with demand=None
        for c_id, c in self.customers.items():
            if c.demand is None:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "NULL_CUSTOMER_DEMAND",
                        f"Customer {c_id} ({c.name!r}) has demand=None. "
                        f"All customers must have a numeric demand value.",
                    )
                )

        return issues

    def _validate_p_constraints(self) -> list[ValidationIssue]:
        """Shared checks for models that enforce exactly p open facilities (p-median, p-cover)."""
        issues: list[ValidationIssue] = []
        total_wh = len(self.warehouses_id)
        if self.num_warehouses > total_wh:
            issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "P_EXCEEDS_TOTAL_WAREHOUSES",
                    f"num_warehouses={self.num_warehouses} but only {total_wh} "
                    f"warehouse(s) exist. Cannot open more facilities than are available.",
                )
            )
        if self.num_warehouses < len(self.force_open):
            issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "P_LESS_THAN_FORCED_OPEN",
                    f"num_warehouses={self.num_warehouses} but {len(self.force_open)} "
                    f"warehouse(s) are in force_open: {self.force_open}. "
                    f"p must be >= len(force_open).",
                )
            )
        return issues

    def _print_issues(self, issues: list[ValidationIssue]) -> None:
        """Print validation issues to console with color coding."""
        for issue in issues:
            color = Colors.RED if issue.severity == Severity.ERROR else Colors.YELLOW
            print(
                f"{color}{Colors.BOLD}[{issue.severity.value}] {issue.message}{Colors.RESET}"
            )

    def build_model(self, is_maximization: bool = False):
        """Build the base optimization model

        Args:
            is_maximization: Whether the objective is to be maximized
        """
        # Pre-solve validation
        issues = self.validate()
        if issues:
            self._print_issues(issues)
            errors = [i for i in issues if i.severity == Severity.ERROR]
            if errors:
                raise ValueError(
                    f"Model has {len(errors)} validation error(s). "
                    f"Fix the issues printed above before solving."
                )

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
            keepFiles=False,
            gapRel=self.gapRel,
            timeLimit=time_limit,
            msg=True,
            options=[
                "preprocess on",  # run CBC’s presolver
                "secHeuristics on",  # enable secondary heuristics
                "cuts on",  # turn on all cut generators
                f"ratioGap {self.gapRel}",  # stop when gap <1%
                "improveStart 1",  # invest more in finding good start solutions
            ],
        )
        self.model.solve(solver=_solver)
        print("OK")

        if pl.LpStatus[self.model.status] == "Optimal":
            print(
                f"==> Optimization Status: {Colors.GREEN}{Colors.BOLD}{pl.LpStatus[self.model.status]} {Colors.RESET} ({self.gapRel} tolerance)<==",
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
                "Flow": self.assignment_vars[w, c].varValue * self.customers[c].demand,
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

            # Demand-weighted percentiles: sort by distance, accumulate demand fraction
            _sorted = df_cu.sort_values("Distance")
            _cum_demand = _sorted["Customer Demand"].cumsum() / _sorted["Customer Demand"].sum()
            _distances = _sorted["Distance"].values
            _cum = _cum_demand.values

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
                "std_customer_distance": df_cu["Distance"].std(),
                "p25_customer_distance": float(np.interp(0.25, _cum, _distances)),
                "p50_customer_distance": float(np.interp(0.50, _cum, _distances)),
                "p75_customer_distance": float(np.interp(0.75, _cum, _distances)),
                "p25_customer_distance_unweighted": df_cu["Distance"].quantile(0.25),
                "p50_customer_distance_unweighted": df_cu["Distance"].quantile(0.50),
                "p75_customer_distance_unweighted": df_cu["Distance"].quantile(0.75),
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

        from netopt_utils import plot_map

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
                " | ".join(
                    [
                        f"ID: {w:3} | City: {self.warehouses[w].city:20} | State: {self.warehouses[w].state:6}",
                        f"Num. customers: {assigned_customers:3} | Outflow: {outflow:11.0f} units",
                        f"Fixed cost: {getattr(self.warehouses[w], 'fixed_cost', 0):10.0f}",
                    ]
                )
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
                f"Std dev of customer distances: {self.solution['std_customer_distance']:.1f} km"
            )
            print(
                f"Percentile distances (demand-weighted): "
                f"P25={self.solution['p25_customer_distance']:.1f} km  "
                f"P50={self.solution['p50_customer_distance']:.1f} km  "
                f"P75={self.solution['p75_customer_distance']:.1f} km"
            )
            print(
                f"Percentile distances (by # customers):  "
                f"P25={self.solution['p25_customer_distance_unweighted']:.1f} km  "
                f"P50={self.solution['p50_customer_distance_unweighted']:.1f} km  "
                f"P75={self.solution['p75_customer_distance_unweighted']:.1f} km"
            )
            print(
                f"Average weighted distance: {self.solution['avg_weighted_distance']:.1f} km"
            )

        # Print multi-sourced customers
        if self.multi_sourced:
            print("\nCustomers served by more than one warehouse")
            for k, v in self.multi_sourced.items():
                print(f"- Customer {k} is served by {v} warehouses")

        self._print_cost_per_unit()

    def _print_cost_per_unit(self):
        """Print cost per unit served (total cost / total demand).

        Uses unit_transport_cost and warehouse fixed costs when available.
        Prints an info message if neither cost component is provided.
        """
        assignments = self.solution.get("customers_assignment", [])
        if not assignments:
            return

        unit_tc = getattr(self, "unit_transport_cost", 0) or 0
        ignore_fc = getattr(self, "ignore_fixed_cost", True)
        has_fixed_costs = not ignore_fc and any(
            (getattr(self.warehouses[w], "fixed_cost", 0) or 0) > 0
            for w in self.active_warehouses
        )
        has_transport_cost = unit_tc > 0

        if not has_transport_cost and not has_fixed_costs:
            print(
                "\nCost per unit served: N/A "
                "(no unit transport cost or facility fixed costs provided)"
            )
            return

        total_demand = sum(rec["Customer Demand"] for rec in assignments)
        if total_demand == 0:
            return

        total_cost = 0.0
        cost_parts = []

        if has_transport_cost:
            transport_cost = (
                sum(rec["Flow"] * rec["Distance"] for rec in assignments) * unit_tc
            )
            total_cost += transport_cost
            cost_parts.append(f"transport: {transport_cost:,.0f}")

        if has_fixed_costs:
            fixed_cost = sum(
                (getattr(self.warehouses[w], "fixed_cost", 0) or 0)
                for w in self.active_warehouses
            )
            total_cost += fixed_cost
            cost_parts.append(f"fixed: {fixed_cost:,.0f}")

        cost_per_unit = total_cost / total_demand
        print(
            f"\nCost per unit served: {cost_per_unit:.4f}"
            f"  ({', '.join(cost_parts)}; total demand: {total_demand:,.0f} units)"
        )


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
        distance: dict | None = None,
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

    def validate(self) -> list[ValidationIssue]:
        issues = NetworkOptimizer.validate(self)
        issues += self._validate_p_constraints()

        # Capacitated p-median: total available capacity < total demand.
        # Only meaningful when ALL non-force_closed warehouses have capacity set;
        # if any are uncapacitated they can absorb unlimited demand.
        if not self.force_uncapacitated:
            non_closed = [
                w
                for w_id, w in self.warehouses.items()
                if w_id not in self.force_closed
            ]
            all_capacitated = all(getattr(w, "capacity", None) for w in non_closed)
            if all_capacitated and non_closed:
                total_capacity = sum(w.capacity for w in non_closed)
                total_demand = sum(
                    c.demand for c in self.customers.values() if c.demand is not None
                )
                if total_capacity < total_demand:
                    issues.append(
                        ValidationIssue(
                            Severity.ERROR,
                            "CAPACITY_INFEASIBLE",
                            f"Total capacity of non-force_closed warehouses ({total_capacity:,.0f}) "
                            f"is less than total customer demand ({total_demand:,.0f}). "
                            f"The capacitated model will be infeasible.",
                        )
                    )

        return issues

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
        assign_uncovered_to_nearest: bool = False,
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
            assign_uncovered_to_nearest: If True, a secondary distance-minimization
                term is added so customers outside high_service_distance are assigned
                to their nearest active facility. The primary coverage objective always
                dominates.
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
        self.assign_uncovered_to_nearest = assign_uncovered_to_nearest

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

    def validate(self) -> list[ValidationIssue]:
        issues = NetworkOptimizer.validate(self)
        issues += self._validate_p_constraints()

        # avg_service_distance sanity: check against best-case lower bound
        if self.avg_service_distance:
            total_demand = sum(
                c.demand for c in self.customers.values() if c.demand is not None
            )
            if total_demand > 0:
                best_case_awd = (
                    sum(
                        min(self.distance[w, c_id] for w in self.warehouses_id)
                        * self.customers[c_id].demand
                        for c_id in self.customers_id
                        if self.customers[c_id].demand is not None
                    )
                    / total_demand
                )
                if self.avg_service_distance < best_case_awd:
                    issues.append(
                        ValidationIssue(
                            Severity.WARNING,
                            "AVG_SERVICE_DIST_TOO_TIGHT",
                            f"avg_service_distance={self.avg_service_distance:.1f} km is smaller than "
                            f"the best-case demand-weighted average distance ({best_case_awd:.1f} km, "
                            f"assuming every customer goes to its nearest facility). "
                            f"This constraint is likely infeasible.",
                        )
                    )

        return issues

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
        total_demand = pl.lpSum([self.customers[c].demand for c in self.customers_id])

        # Primary: maximize fraction of demand covered within high_service_distance
        primary = (
            pl.lpSum(
                [
                    self.customers[c].demand
                    * self.high_service_dist_par[w, c]
                    * self.assignment_vars[w, c]
                    for w in self.warehouses_id
                    for c in self.customers_id
                ]
            )
            / total_demand
        )

        if self.assign_uncovered_to_nearest:
            # Secondary: minimize distance for assignments outside high_service_distance.
            # ε is chosen so that covering one more customer always beats any distance saving:
            #   ε · |customers| < min_demand / total_demand
            total_dem = sum(self.customers[c].demand for c in self.customers_id)
            min_dem = min(self.customers[c].demand for c in self.customers_id)
            out_of_coverage = [
                (w, c)
                for w in self.warehouses_id
                for c in self.customers_id
                if self.high_service_dist_par[w, c] == 0
            ]
            if out_of_coverage:
                max_dist = max(self.distance[w, c] for w, c in out_of_coverage)
                epsilon = 0.9 * min_dem / (len(self.customers_id) * total_dem)
                secondary = pl.lpSum(
                    [
                        (self.distance[w, c] / max_dist) * self.assignment_vars[w, c]
                        for w, c in out_of_coverage
                    ]
                )
                self.model.setObjective(primary - epsilon * secondary)
                return

        self.model.setObjective(primary)

    def _get_plot_options(self):
        """Get options for plotting P-Cover model"""
        return {"radius": self.high_service_distance}

    def print_solution_details(self):
        """Print P-Cover specific solution details"""
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return

        print("P-Cover optimization results:")
        print(
            f"% covered demand within {self.high_service_distance} distance: "
            f"{round(self.solution['objective_value'] * 100, 1)}%"
        )

        # Print common solution details
        super().print_solution_details()


class TotalCoverOptimizer(NetworkOptimizer):
    """Total Cover optimization model

    Finds the minimum number of facilities needed to cover all customers
    within a specified coverage radius.
    """

    def __init__(
        self,
        objective: str,
        warehouses: dict,
        customers: dict,
        distance: dict,
        coverage_distance: float,
        **kwargs,
    ):
        """Initialize Total Cover optimizer

        Args:
            warehouses: Dictionary of warehouse objects
            customers: Dictionary of customer objects
            distance: Distance matrix
            coverage_distance: Radius within which a warehouse covers a customer
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(
            objective=objective,
            warehouses=warehouses,
            customers=customers,
            distance=distance,
            **kwargs,
        )
        self.coverage_distance = coverage_distance

        # Precompute binary coverage parameters
        self.coverage_par = {
            (w, c): 1 if self.distance[w, c] <= self.coverage_distance else 0
            for w in self.warehouses_id
            for c in self.customers_id
        }

    def validate(self) -> list[ValidationIssue]:
        issues = NetworkOptimizer.validate(self)

        # Coverage radius too small: at least one customer can't reach any warehouse
        for c_id in self.customers_id:
            min_dist = min(self.distance[w, c_id] for w in self.warehouses_id)
            if min_dist > self.coverage_distance:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "TOTALCOVER_RADIUS_TOO_SMALL",
                        f"Coverage radius {self.coverage_distance:.1f} km is too small: "
                        f"customer {c_id} ({self.customers[c_id].name!r}) is at least "
                        f"{min_dist:.1f} km from every warehouse and cannot be covered. "
                        f"Minimum feasible radius: "
                        f"{max(min(self.distance[w, c] for w in self.warehouses_id) for c in self.customers_id):.1f} km.",
                    )
                )
                break  # one example is enough

        return issues

    def build_model(self, is_maximization: bool = False):
        """Build the Total Cover optimization model (always minimization)"""
        super().build_model(is_maximization=False)

        # Restrict assignments: a customer can only be served by a warehouse within coverage radius
        for w in self.warehouses_id:
            for c in self.customers_id:
                self.assignment_vars[w, c].upBound = self.coverage_par[w, c]

        self.set_objective()

    def set_objective(self):
        """Minimize total number of open warehouses"""
        print("- Objective function: minimize number of open warehouses")
        self.model.setObjective(
            pl.lpSum([self.facility_status_vars[w] for w in self.warehouses_id])
        )

    def _get_plot_options(self):
        return {"radius": self.coverage_distance}

    def print_solution_details(self):
        """Print Total Cover specific solution details"""
        if not self.solution:
            print("No solution available. Please solve the model first.")
            return

        print("Total Cover optimization results:")
        print(
            f"Minimum warehouses to cover all demand within {self.coverage_distance} km: "
            f"{int(self.solution['objective_value'])}"
        )

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

    def validate(self) -> list[ValidationIssue]:
        issues = NetworkOptimizer.validate(self)

        # Total capacity of non-force_closed warehouses vs total demand.
        # Only meaningful when ALL non-force_closed warehouses have capacity set;
        # if any are uncapacitated they can absorb unlimited demand.
        non_closed = [
            w for w_id, w in self.warehouses.items() if w_id not in self.force_closed
        ]
        all_capacitated = all(getattr(w, "capacity", None) for w in non_closed)
        if all_capacitated and non_closed:
            total_capacity = sum(w.capacity for w in non_closed)
            total_demand = sum(
                c.demand for c in self.customers.values() if c.demand is not None
            )
            if total_capacity < total_demand:
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "CAPACITY_INFEASIBLE",
                        f"Total capacity of non-force_closed warehouses ({total_capacity:,.0f}) "
                        f"is less than total customer demand ({total_demand:,.0f}). "
                        f"The model will be infeasible.",
                    )
                )

        # Per forced-allocation: demand[c] > capacity[w]
        for w_id, c_id in self.force_allocations:
            if w_id not in self.warehouses_id or c_id not in self.customers_id:
                continue  # already reported by base validate()
            w = self.warehouses[w_id]
            c = self.customers[c_id]
            if (
                getattr(w, "capacity", None)
                and c.demand is not None
                and c.demand > w.capacity
            ):
                issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "FORCE_ALLOC_DEMAND_EXCEEDS_CAPACITY",
                        f"force_allocations: customer {c_id} ({c.name!r}) has demand "
                        f"{c.demand:,.0f} which exceeds capacity {w.capacity:,.0f} "
                        f"of warehouse {w_id} ({w.name!r}).",
                    )
                )

        # Warehouses with no capacity set in CFLP (will be silently excluded)
        null_cap = [
            w_id
            for w_id, w in self.warehouses.items()
            if not getattr(w, "capacity", None)
        ]
        if null_cap:
            issues.append(
                ValidationIssue(
                    Severity.WARNING,
                    "WAREHOUSES_WITHOUT_CAPACITY",
                    f"{len(null_cap)} warehouse(s) have no capacity set and will be excluded "
                    f"from the CFLP model: {null_cap}.",
                )
            )

        return issues

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
