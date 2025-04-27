import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from netopt_compat import netopt


class TestNetoptCompat:
    """Tests for the backward compatibility netopt wrapper function"""

    @patch("netopt_compat.solve_network_optimization")
    def test_netopt_wrapper_p_median(
        self,
        mock_solve_network_optimization,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test that netopt forwards p-median calls correctly to solve_network_optimization"""
        # Set up mock return value
        mock_solution = {"status": "Optimal", "objective_value": 100}
        mock_solve_network_optimization.return_value = mock_solution

        # Call the netopt function with p-median parameters
        result = netopt(
            num_warehouses=3,
            factories=None,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            objective="mindistance",
            plot=False,
        )

        # Check that solve_network_optimization was called with the correct parameters
        mock_solve_network_optimization.assert_called_once()
        args, kwargs = mock_solve_network_optimization.call_args
        assert kwargs["objective"] == "mindistance"
        assert kwargs["num_warehouses"] == 3
        assert kwargs["warehouses"] == small_test_warehouses
        assert kwargs["customers"] == small_test_customers
        assert kwargs["distance"] == small_test_distance
        assert kwargs["plot"] is False

        # Check that the return value was correctly forwarded
        assert result == mock_solution

    @patch("netopt_compat.solve_network_optimization")
    def test_netopt_wrapper_p_cover(
        self,
        mock_solve_network_optimization,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test that netopt forwards p-cover calls correctly to solve_network_optimization"""
        # Set up mock return value
        mock_solution = {"status": "Optimal", "objective_value": 0.85}
        mock_solve_network_optimization.return_value = mock_solution

        # Call the netopt function with p-cover parameters
        result = netopt(
            num_warehouses=2,
            factories=None,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            objective="maxcover",
            high_service_distance=1000,
            avg_service_distance=1500,
            plot=True,
            plot_size=(12, 10),
            hide_inactive=True,
        )

        # Check that solve_network_optimization was called with the correct parameters
        mock_solve_network_optimization.assert_called_once()
        args, kwargs = mock_solve_network_optimization.call_args
        assert kwargs["objective"] == "maxcover"
        assert kwargs["num_warehouses"] == 2
        assert kwargs["high_service_distance"] == 1000
        assert kwargs["avg_service_distance"] == 1500
        assert kwargs["plot"] is True
        assert kwargs["plot_size"] == (12, 10)
        assert kwargs["hide_inactive"] is True

        # Check that the return value was correctly forwarded
        assert result == mock_solution

    @patch("netopt_compat.solve_network_optimization")
    def test_netopt_wrapper_flp(
        self,
        mock_solve_network_optimization,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test that netopt forwards FLP calls correctly to solve_network_optimization"""
        # Set up mock return value
        mock_solution = {"status": "Optimal", "objective_value": 12345.6}
        mock_solve_network_optimization.return_value = mock_solution

        # Call the netopt function with FLP parameters (mincost objective)
        result = netopt(
            num_warehouses=0,  # Unconstrained number of warehouses for FLP
            factories=None,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            objective="mincost",
            force_uncapacitated=True,
            ignore_fixed_cost=True,
            unit_transport_cost=0.2,
            mutually_exclusive=[(1, 2), (3, 4)],
        )

        # Check that solve_network_optimization was called with the correct parameters
        mock_solve_network_optimization.assert_called_once()
        args, kwargs = mock_solve_network_optimization.call_args
        assert kwargs["objective"] == "mincost"
        assert kwargs["num_warehouses"] == 0
        assert kwargs["force_uncapacitated"] is True
        assert kwargs["ignore_fixed_cost"] is True
        assert kwargs["unit_transport_cost"] == 0.2
        assert kwargs["mutually_exclusive"] == [(1, 2), (3, 4)]

        # Check that the return value was correctly forwarded
        assert result == mock_solution

    @patch("netopt_compat.solve_network_optimization")
    def test_netopt_wrapper_with_factories(
        self,
        mock_solve_network_optimization,
        small_test_warehouses,
        small_test_customers,
        small_test_distance,
    ):
        """Test that netopt correctly forwards the factories parameter"""
        # Create mock factories
        mock_factories = {1: MagicMock(), 2: MagicMock()}

        # Set up mock return value
        mock_solution = {"status": "Optimal", "objective_value": 100}
        mock_solve_network_optimization.return_value = mock_solution

        # Call the netopt function with factories
        result = netopt(
            num_warehouses=2,
            factories=mock_factories,
            warehouses=small_test_warehouses,
            customers=small_test_customers,
            distance=small_test_distance,
            objective="mindistance",
        )

        # Check that solve_network_optimization was called with the correct factories
        mock_solve_network_optimization.assert_called_once()
        args, kwargs = mock_solve_network_optimization.call_args
        assert kwargs["factories"] == mock_factories
