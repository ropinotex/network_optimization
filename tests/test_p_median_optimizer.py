import pytest
import pulp as pl
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network_optimizer import PMedianOptimizer


class TestPMedianOptimizer:
    """Tests for the PMedianOptimizer class"""

    def test_init(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization of PMedianOptimizer"""
        optimizer = PMedianOptimizer(
            num_warehouses=3,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        # Check initialization
        assert optimizer.num_warehouses == 3
        assert len(optimizer.warehouses) == 5
        assert len(optimizer.customers) == 8

    def test_build_model(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test build_model method specific to PMedianOptimizer"""
        optimizer = PMedianOptimizer(
            num_warehouses=3,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()

        # Check model was created properly
        assert optimizer.model is not None
        assert optimizer.model.sense == 1  # PuLP.LpMinimize

        # Check p-median specific constraints
        p_constraint_found = False
        for name, constraint in optimizer.model.constraints.items():
            if name == "Num_of_active_warehouses":
                p_constraint_found = True
                # Check RHS is equal to num_warehouses (3)
                assert constraint.constant == 3

        # P-median should have exactly p warehouses constraint
        assert p_constraint_found, "No constraint for number of active warehouses found"

    def test_set_objective(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test that set_objective creates the weighted distance objective"""
        optimizer = PMedianOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()

        # The objective should be a minimization problem
        assert optimizer.model.sense == 1  # PuLP.LpMinimize

        # Check objective function was set correctly
        # (We can't check the exact formula easily, but we can check some properties)
        assert optimizer.model.objective is not None

    @patch("pulp.LpProblem.solve")
    def test_p_median_solution(
        self,
        mock_solve,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test solution extraction for p-median"""
        # Set up mock solver response
        mock_solve.return_value = 1  # Optimal

        # Create test variables to simulate a solution
        optimizer = PMedianOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()

        # Manually set the solution values to simulate a solve
        # Warehouses 1 and 3 are open
        for w in optimizer.warehouses_id:
            optimizer.facility_status_vars[w].varValue = 1 if w in [1, 3] else 0

        # Assign customers to warehouses
        for w, c in optimizer.assignment_vars:
            if w == 1 and c in [1, 7]:  # NY serves Philadelphia and Jacksonville
                optimizer.assignment_vars[w, c].varValue = 1
            elif w == 3 and c in [
                2,
                3,
                4,
                5,
                6,
                8,
            ]:  # Chicago serves the other customers
                optimizer.assignment_vars[w, c].varValue = 1
            else:
                optimizer.assignment_vars[w, c].varValue = 0

        # Mock the model's objective value
        optimizer.model.objective.value = lambda: 1234.56

        # Extract solution information
        optimizer._extract_solution()
        optimizer._analyze_solution()

        # Check solution extraction
        assert len(optimizer.active_warehouses) == 2
        assert 1 in optimizer.active_warehouses  # New York
        assert 3 in optimizer.active_warehouses  # Chicago
        assert len(optimizer.flows) == 8  # All customers are assigned

        # Verify customer assignments
        customer_assignments = set()
        for w, c in optimizer.flows:
            customer_assignments.add(c)

        # All customers should be assigned
        assert len(customer_assignments) == 8
        assert set(customer_assignments) == set(range(1, 9))

    def test_print_solution_details(
        self, small_test_warehouses, small_test_customers, small_test_distance, capsys
    ):
        """Test that print_solution_details outputs correctly"""
        optimizer = PMedianOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        # Set a mock solution
        optimizer.solution = {
            "status": "Optimal",
            "objective_value": 1234.56,
            "active_warehouses_id": {1, 3},
            "active_warehouses_name": ["New York, NY", "Chicago, IL"],
            "multi_sourced_customers": [],
        }

        optimizer.active_warehouses = {1, 3}
        optimizer.multi_sourced = {}

        # Mock the assignment_vars dictionary with dummy objects
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

        optimizer.print_solution_details()
        captured = capsys.readouterr()

        # Check that the output contains the expected information
        assert "P-Median optimization results" in captured.out
        assert "Average weighted distance: 1234.6" in captured.out
        assert "Open warehouses: (2 out of 5)" in captured.out
        assert "New York" in captured.out
        assert "Chicago" in captured.out
