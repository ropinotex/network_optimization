import pytest
import pulp as pl
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network_optimizer import UncapacitatedFLPOptimizer, CapacitatedFLPOptimizer


class TestUncapacitatedFLPOptimizer:
    """Tests for the UncapacitatedFLPOptimizer class"""

    def test_init(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization of UncapacitatedFLPOptimizer"""
        optimizer = UncapacitatedFLPOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            unit_transport_cost=0.2,
        )

        # Check initialization
        assert len(optimizer.warehouses) == 5
        assert len(optimizer.customers) == 8
        assert optimizer.unit_transport_cost == 0.2
        assert optimizer.ignore_fixed_cost is False
        # Should be forced to uncapacitated
        assert optimizer.force_uncapacitated is True

    def test_build_model(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test build_model method for UncapacitatedFLPOptimizer"""
        optimizer = UncapacitatedFLPOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()

        # Check model was created properly
        assert optimizer.model is not None
        assert optimizer.model.sense == 1  # PuLP.LpMinimize

        # In FLP, there shouldn't be a constraint on the number of warehouses
        for name in optimizer.model.constraints:
            assert name != "Num_of_active_warehouses", (
                "FLP should not have a fixed number of warehouses constraint"
            )

        # No capacity constraints should be added
        for name in optimizer.model.constraints:
            assert not name.startswith("Capacity_limit_warehouse_"), (
                "Uncapacitated FLP should not have capacity constraints"
            )

    def test_set_objective_with_fixed_cost(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test that set_objective includes fixed costs"""
        optimizer = UncapacitatedFLPOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            unit_transport_cost=0.1,
            ignore_fixed_cost=False,
        )

        optimizer.build_model()

        # The objective should be a minimization problem
        assert optimizer.model.sense == 1  # PuLP.LpMinimize
        assert optimizer.model.objective is not None

        # Hard to check exact objective function, but we can verify some properties
        # by checking the coefficients in the objective for facility_status_vars

        # For uncapacitated with fixed costs, warehouse status vars should have coefficients
        # equal to their fixed costs
        for w in optimizer.warehouses_id:
            found_fixed_cost = False
            for term in optimizer.model.objective.items():
                if term[0] is optimizer.facility_status_vars[w]:
                    found_fixed_cost = True
                    break
            assert found_fixed_cost, (
                f"Fixed cost for warehouse {w} not found in objective"
            )

    def test_set_objective_ignore_fixed_cost(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test that set_objective ignores fixed costs when requested"""
        optimizer = UncapacitatedFLPOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            unit_transport_cost=0.1,
            ignore_fixed_cost=True,
        )

        optimizer.build_model()

        # The objective should be a minimization problem
        assert optimizer.model.sense == 1  # PuLP.LpMinimize
        assert optimizer.model.objective is not None

        # For uncapacitated without fixed costs, warehouse status vars should not have coefficients
        for w in optimizer.warehouses_id:
            for term in optimizer.model.objective.items():
                if term[0] is optimizer.facility_status_vars[w]:
                    assert term[1] == 0, (
                        f"Fixed cost for warehouse {w} found in objective despite ignore_fixed_cost=True"
                    )

    def test_print_solution_details(
        self, small_test_warehouses, small_test_customers, small_test_distance, capsys
    ):
        """Test that print_solution_details outputs correctly"""
        optimizer = UncapacitatedFLPOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            unit_transport_cost=0.1,
        )

        # Set a mock solution
        optimizer.solution = {
            "status": "Optimal",
            "objective_value": 12345.6,
            "active_warehouses_id": {1, 3},
            "active_warehouses_name": ["New York, NY", "Chicago, IL"],
            "multi_sourced_customers": [],
        }

        optimizer.active_warehouses = {1, 3}
        optimizer.multi_sourced = {}

        # Mock the assignment_vars and facility_status_vars dictionaries
        class DummyVar:
            def __init__(self, val):
                self.varValue = val

        optimizer.assignment_vars = {}
        for w in [1, 3]:
            for c in range(1, 9):
                if (w == 1 and c in [1, 7]) or (w == 3 and c in [2, 3, 4, 5, 6, 8]):
                    optimizer.assignment_vars[w, c] = DummyVar(1)
                else:
                    optimizer.assignment_vars[w, c] = DummyVar(0)

        optimizer.facility_status_vars = {}
        for w in range(1, 6):
            optimizer.facility_status_vars[w] = DummyVar(1 if w in [1, 3] else 0)

        optimizer.print_solution_details()
        captured = capsys.readouterr()

        # Check that the output contains the expected information
        assert "Uncapacitated FLP optimization results" in captured.out
        assert "Total cost: 12346" in captured.out
        assert "Open warehouses: (2 out of 5)" in captured.out


class TestCapacitatedFLPOptimizer:
    """Tests for the CapacitatedFLPOptimizer class"""

    def test_init(
        self, capacitated_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization of CapacitatedFLPOptimizer"""
        optimizer = CapacitatedFLPOptimizer(
            warehouses=capacitated_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            unit_transport_cost=0.2,
        )

        # Check initialization
        assert len(optimizer.warehouses) == 5
        assert len(optimizer.customers) == 8
        assert optimizer.unit_transport_cost == 0.2
        assert optimizer.ignore_fixed_cost is False
        # Should NOT be forced to uncapacitated
        assert optimizer.force_uncapacitated is False

    def test_build_model(
        self, capacitated_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test build_model method for CapacitatedFLPOptimizer"""
        optimizer = CapacitatedFLPOptimizer(
            warehouses=capacitated_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()

        # Check model was created properly
        assert optimizer.model is not None
        assert optimizer.model.sense == 1  # PuLP.LpMinimize

        # Count capacity constraints
        capacity_constraints = 0
        for name in optimizer.model.constraints:
            if name.startswith("Capacity_limit_warehouse_"):
                capacity_constraints += 1

        # Capacitated FLP should have capacity constraints
        assert capacity_constraints == 5, (
            "Capacitated FLP should have capacity constraints"
        )

    def test_print_solution_details(
        self,
        capacitated_test_warehouses,
        small_test_customers,
        small_test_distance,
        capsys,
    ):
        """Test that print_solution_details outputs correctly with capacity utilization"""
        optimizer = CapacitatedFLPOptimizer(
            warehouses=capacitated_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            unit_transport_cost=0.1,
        )

        # Set a mock solution
        optimizer.solution = {
            "status": "Optimal",
            "objective_value": 12345.6,
            "active_warehouses_id": {1, 3},
            "active_warehouses_name": ["New York, NY", "Chicago, IL"],
            "multi_sourced_customers": [],
        }

        optimizer.active_warehouses = {1, 3}
        optimizer.multi_sourced = {}

        # Mock the assignment_vars and facility_status_vars dictionaries
        class DummyVar:
            def __init__(self, val):
                self.varValue = val

        # Setup assignments - customer 1 to warehouse 1, all others to warehouse 3
        # This will give warehouse 1 a demand of 100 and warehouse 3 a demand of 1080
        optimizer.assignment_vars = {}
        for w in range(1, 6):
            for c in range(1, 9):
                if w == 1 and c == 1:  # NY serves Philadelphia
                    optimizer.assignment_vars[w, c] = DummyVar(1)
                elif w == 3 and c > 1:  # Chicago serves all other customers
                    optimizer.assignment_vars[w, c] = DummyVar(1)
                else:
                    optimizer.assignment_vars[w, c] = DummyVar(0)

        optimizer.facility_status_vars = {}
        for w in range(1, 6):
            optimizer.facility_status_vars[w] = DummyVar(1 if w in [1, 3] else 0)

        optimizer.print_solution_details()
        captured = capsys.readouterr()

        # Check that the output contains the expected information
        assert "Capacitated FLP optimization results" in captured.out
        assert "Total cost: 12346" in captured.out
        assert "Open warehouses: (2 out of 5)" in captured.out
        assert "Warehouse capacity utilization:" in captured.out

        # Capacity utilization:
        # - NY warehouse has capacity 300, using 100 units (33.3%)
        # - Chicago warehouse has capacity 400, using 980 units (245%)
        assert "Warehouse 1:" in captured.out  # NY capacity usage
        assert "Warehouse 3:" in captured.out  # Chicago capacity usage
