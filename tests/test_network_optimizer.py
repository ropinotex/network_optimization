import pytest
import pulp as pl
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network_optimizer import NetworkOptimizer


# Create a concrete subclass of NetworkOptimizer for testing
class TestableNetworkOptimizer(NetworkOptimizer):
    """Concrete implementation of NetworkOptimizer for testing"""

    def set_objective(self):
        """Implementation of abstract method"""
        # Simple objective: minimize sum of distances
        total_distance = pl.lpSum(
            [
                self.distance[w, c] * self.assignment_vars[w, c]
                for w in self.warehouses_id
                for c in self.customers_id
            ]
        )
        self.model.setObjective(total_distance)


class TestNetworkOptimizer:
    """Tests for the NetworkOptimizer base class functionality"""

    def test_init(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization of NetworkOptimizer with minimal parameters"""
        optimizer = TestableNetworkOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        # Check initialization
        assert len(optimizer.warehouses) == 5
        assert len(optimizer.customers) == 8
        assert len(optimizer.distance) == 40  # 5 warehouses * 8 customers
        assert optimizer.force_single_sourcing is True
        assert optimizer.force_uncapacitated is False

    def test_init_with_options(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test initialization with additional options"""
        optimizer = TestableNetworkOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            force_single_sourcing=False,
            force_uncapacitated=True,
            force_open=[1, 3],
            force_closed=[2, 4],
            distance_ranges=[0, 500, 1000, 3000],
            mutually_exclusive=[(1, 2), (3, 4)],
        )

        # Check options were properly set
        assert optimizer.force_single_sourcing is False
        assert optimizer.force_uncapacitated is True
        assert optimizer.force_open == [1, 3]
        assert optimizer.force_closed == [2, 4]
        assert optimizer.distance_ranges == [0, 500, 1000, 3000, 99999]
        assert optimizer.mutually_exclusive == [(1, 2), (3, 4)]

    def test_build_model_minimization(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test building a minimization model"""
        optimizer = TestableNetworkOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model(is_maximization=False)

        # Check model was created properly
        assert optimizer.model is not None
        assert optimizer.model.sense == 1  # PuLP.LpMinimize
        assert optimizer.facility_status_vars is not None
        assert optimizer.assignment_vars is not None

        # Check variables are created for each warehouse and customer
        assert len(optimizer.facility_status_vars) == 5  # 5 warehouses
        assert len(optimizer.assignment_vars) == 40  # 5 warehouses * 8 customers

    def test_build_model_maximization(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test building a maximization model"""
        optimizer = TestableNetworkOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model(is_maximization=True)

        assert optimizer.model is not None
        assert optimizer.model.sense == -1  # PuLP.LpMaximize

    def test_add_capacity_constraints(
        self, capacitated_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test adding capacity constraints"""
        optimizer = TestableNetworkOptimizer(
            warehouses=capacitated_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()

        # Count capacity constraints by checking the model constraints
        capacity_constraints = 0
        for name, constraint in optimizer.model.constraints.items():
            if name.startswith("Capacity_limit_warehouse_"):
                capacity_constraints += 1

        assert capacity_constraints == 5  # One for each warehouse

    def test_force_uncapacitated(
        self, capacitated_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test that force_uncapacitated=True prevents capacity constraints"""
        optimizer = TestableNetworkOptimizer(
            warehouses=capacitated_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            force_uncapacitated=True,
        )

        optimizer.build_model()

        # No capacity constraints should be added
        for name in optimizer.model.constraints:
            assert not name.startswith("Capacity_limit_warehouse_")

    @patch("pulp.LpProblem.solve")
    def test_solve(
        self,
        mock_solve,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test the solve method"""
        # Setup the mock
        mock_solve.return_value = 1  # PuLP.LpStatusOptimal

        optimizer = TestableNetworkOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()
        result = optimizer.solve(solver_log=True)

        # Check that solve was called
        assert mock_solve.called

    @patch("pulp.LpProblem.solve")
    @patch("pulp.LpStatus")
    def test_solve_infeasible(
        self,
        mock_status,
        mock_solve,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test handling of infeasible solutions"""
        # Setup the mocks
        mock_solve.return_value = 0
        mock_status.__getitem__.return_value = "Infeasible"

        optimizer = TestableNetworkOptimizer(
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
        )

        optimizer.build_model()
        result = optimizer.solve()

        # Should return None for infeasible models
        assert result is None
