import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network_factory import create_network_optimizer, solve_network_optimization
from network_optimizer import (
    PMedianOptimizer,
    PCoverOptimizer,
    UncapacitatedFLPOptimizer,
    CapacitatedFLPOptimizer,
)


class TestNetworkFactory:
    """Tests for the network_factory module"""

    def test_create_network_optimizer_p_median(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test creating a PMedianOptimizer"""
        optimizer = create_network_optimizer(
            objective="mindistance",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            num_warehouses=3,
        )

        # Check that the correct type of optimizer was created
        assert isinstance(optimizer, PMedianOptimizer)
        assert optimizer.num_warehouses == 3

    def test_create_network_optimizer_p_cover(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test creating a PCoverOptimizer"""
        optimizer = create_network_optimizer(
            objective="maxcover",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            num_warehouses=3,
            high_service_distance=1000,
        )

        # Check that the correct type of optimizer was created
        assert isinstance(optimizer, PCoverOptimizer)
        assert optimizer.num_warehouses == 3
        assert optimizer.high_service_distance == 1000

    def test_create_network_optimizer_uncapacitated_flp(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test creating an UncapacitatedFLPOptimizer"""
        optimizer = create_network_optimizer(
            objective="mincost",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            force_uncapacitated=True,
        )

        # Check that the correct type of optimizer was created
        assert isinstance(optimizer, UncapacitatedFLPOptimizer)
        assert optimizer.force_uncapacitated is True

    def test_create_network_optimizer_capacitated_flp(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test creating a CapacitatedFLPOptimizer"""
        optimizer = create_network_optimizer(
            objective="mincost",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            force_uncapacitated=False,
        )

        # Check that the correct type of optimizer was created
        assert isinstance(optimizer, CapacitatedFLPOptimizer)
        assert optimizer.force_uncapacitated is False

    def test_create_network_optimizer_with_options(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test creating an optimizer with additional options"""
        optimizer = create_network_optimizer(
            objective="mindistance",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            num_warehouses=2,
            force_single_sourcing=False,
            force_open=[1, 3],
            force_closed=[2, 4],
        )

        # Check that options were correctly passed to the optimizer
        assert isinstance(optimizer, PMedianOptimizer)
        assert optimizer.force_single_sourcing is False
        assert optimizer.force_open == [1, 3]
        assert optimizer.force_closed == [2, 4]

    def test_create_network_optimizer_invalid_objective(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test error when invalid objective is provided"""
        with pytest.raises(ValueError, match="Unknown objective"):
            create_network_optimizer(
                objective="invalid",
                warehouses=small_test_warehouses,
                customers=small_test_customers,
                distance=small_test_distance,
            )

    def test_create_network_optimizer_p_median_missing_num_warehouses(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test error when num_warehouses is missing for p-median"""
        with pytest.raises(ValueError, match="num_warehouses must be specified"):
            create_network_optimizer(
                objective="mindistance",
                warehouses=small_test_warehouses,
                customers=small_test_customers,
                distance=small_test_distance,
            )

    def test_create_network_optimizer_p_cover_missing_params(
        self, small_test_warehouses, small_test_customers, small_test_distance
    ):
        """Test error when required parameters are missing for p-cover"""
        with pytest.raises(ValueError, match="num_warehouses must be specified"):
            create_network_optimizer(
                objective="maxcover",
                warehouses=small_test_warehouses,
                customers=small_test_customers,
                distance=small_test_distance,
                high_service_distance=1000,
            )

        with pytest.raises(ValueError, match="high_service_distance must be specified"):
            create_network_optimizer(
                objective="maxcover",
                warehouses=small_test_warehouses,
                customers=small_test_customers,
                distance=small_test_distance,
                num_warehouses=3,
            )

    @patch("network_factory.create_network_optimizer")
    def test_solve_network_optimization(
        self,
        mock_create_optimizer,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test solve_network_optimization function"""
        # Create a mock optimizer
        mock_optimizer = MagicMock()
        mock_optimizer.solve.return_value = {
            "status": "Optimal",
            "objective_value": 100,
        }
        mock_create_optimizer.return_value = mock_optimizer

        # Call the function
        result = solve_network_optimization(
            objective="mindistance",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            num_warehouses=3,
            plot=True,
            hide_inactive=True,
            hide_flows=True,
            plot_size=(10, 10),
            solver_log=True,
        )

        # Check that create_network_optimizer was called with the right parameters
        mock_create_optimizer.assert_called_once_with(
            objective="mindistance",
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            num_warehouses=3,
        )

        # Check that the optimizer's methods were called
        assert mock_optimizer.build_model.called
        assert mock_optimizer.solve.called
        assert mock_optimizer.print_solution_details.called
        assert mock_optimizer.plot_solution.called

        # Check that the solution was returned
        assert result == {"status": "Optimal", "objective_value": 100}
