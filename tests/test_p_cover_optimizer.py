import pytest
import pulp as pl
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network_optimizer import PCoverOptimizer


class TestPCoverOptimizer:
    """Tests for the PCoverOptimizer class"""

    def test_init(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization of PCoverOptimizer"""
        optimizer = PCoverOptimizer(
            num_warehouses=3,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
        )

        # Check initialization
        assert optimizer.num_warehouses == 3
        assert optimizer.high_service_distance == 1000
        assert optimizer.max_service_distance == 99999  # Default
        assert len(optimizer.warehouses) == 5
        assert len(optimizer.customers) == 8

        # Check high service distance parameters
        assert len(optimizer.high_service_dist_par) == 40  # 5 warehouses * 8 customers

        # Check a few values in the high_service_dist_par dictionary
        # New York (wh 1) to Philadelphia (cust 1): 80km, within 1000km
        assert optimizer.high_service_dist_par[(1, 1)] == 1

        # Los Angeles (wh 2) to Philadelphia (cust 1): 4500km, outside 1000km
        assert optimizer.high_service_dist_par[(2, 1)] == 0

    def test_init_with_max_service_distance(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization with max_service_distance"""
        optimizer = PCoverOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
            max_service_distance=2000,
        )

        # Check initialization
        assert optimizer.max_service_distance == 2000

        # Check max service distance parameters
        assert len(optimizer.max_service_dist_par) == 40  # 5 warehouses * 8 customers

        # Check a few values in the max_service_dist_par dictionary
        # New York (wh 1) to Philadelphia (cust 1): 80km, within 2000km
        assert optimizer.max_service_dist_par[(1, 1)] == 1

        # Los Angeles (wh 2) to Philadelphia (cust 1): 4500km, outside 2000km
        assert optimizer.max_service_dist_par[(2, 1)] == 0

        # Chicago (wh 3) to San Antonio (cust 2): 1700km, within 2000km
        assert optimizer.max_service_dist_par[(3, 2)] == 1

    def test_build_model(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test build_model method specific to PCoverOptimizer"""
        optimizer = PCoverOptimizer(
            num_warehouses=3,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
        )

        optimizer.build_model()

        # Check model was created properly
        assert optimizer.model is not None
        assert optimizer.model.sense == -1  # PuLP.LpMaximize (p-cover is maximization)

        # Check p-cover specific constraints (number of warehouses constraint)
        p_constraint_found = False
        for name, constraint in optimizer.model.constraints.items():
            if name == "Num_of_active_warehouses":
                p_constraint_found = True
                # Check RHS is equal to num_warehouses (3)
                assert constraint.constant == 3

        assert p_constraint_found, "No constraint for number of active warehouses found"

        # Check that assignment variable bounds were updated based on max_service_dist_par
        for w, c in optimizer.assignment_vars:
            assert (
                optimizer.assignment_vars[w, c].upBound
                == optimizer.max_service_dist_par[w, c]
            )

    def test_with_avg_service_distance(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test with average service distance constraint"""
        optimizer = PCoverOptimizer(
            num_warehouses=3,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
            avg_service_distance=1500,
        )

        optimizer.build_model()

        # Check for the average service distance constraint
        avg_constraint_found = False
        for name, constraint in optimizer.model.constraints.items():
            if name == "Avoid_random_allocations":
                avg_constraint_found = True

        assert avg_constraint_found, "No constraint for average service distance found"

    def test_set_objective(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test that set_objective creates the proper objective for p-cover"""
        optimizer = PCoverOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
        )

        optimizer.build_model()

        # The objective should be a maximization problem
        assert optimizer.model.sense == -1  # PuLP.LpMaximize

        # Check objective function was set
        assert optimizer.model.objective is not None

    def test_get_plot_options(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test that _get_plot_options returns the high service distance"""
        optimizer = PCoverOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
        )

        plot_options = optimizer._get_plot_options()
        assert plot_options == {"radius": 1000}

    def test_print_solution_details(
        self, small_test_warehouses, small_test_customers, small_test_distance, capsys
    ):
        """Test that print_solution_details outputs correctly for p-cover"""
        optimizer = PCoverOptimizer(
            num_warehouses=2,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            high_service_distance=1000,
        )

        # Set a mock solution
        optimizer.solution = {
            "status": "Optimal",
            "objective_value": 0.85,  # 85% covered
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
        assert "P-Cover optimization results" in captured.out
        assert "% covered demand within 1000 distance: 85.0%" in captured.out
        assert "Open warehouses: (2 out of 5)" in captured.out
