import pytest
from collections import namedtuple
import numpy as np


# Create simple classes for test data similar to actual structures
class Warehouse:
    def __init__(
        self, id, city, state, latitude, longitude, capacity=None, fixed_cost=1000
    ):
        self.id = id
        self.city = city
        self.state = state
        self.name = f"{city}, {state}"
        self.latitude = latitude
        self.longitude = longitude
        self.capacity = capacity
        self.fixed_cost = fixed_cost


class Customer:
    def __init__(self, id, city, state, latitude, longitude, demand):
        self.id = id
        self.city = city
        self.state = state
        self.name = f"{city}, {state}"
        self.latitude = latitude
        self.longitude = longitude
        self.demand = demand


@pytest.fixture
def small_test_warehouses():
    """Fixture providing a small set of warehouses for testing"""
    warehouses = {
        1: Warehouse(1, "New York", "NY", 40.7128, -74.0060),
        2: Warehouse(2, "Los Angeles", "CA", 34.0522, -118.2437),
        3: Warehouse(3, "Chicago", "IL", 41.8781, -87.6298),
        4: Warehouse(4, "Houston", "TX", 29.7604, -95.3698),
        5: Warehouse(5, "Phoenix", "AZ", 33.4484, -112.0740),
    }
    return warehouses


@pytest.fixture
def small_test_customers():
    """Fixture providing a small set of customers for testing"""
    customers = {
        1: Customer(1, "Philadelphia", "PA", 39.9526, -75.1652, 100),
        2: Customer(2, "San Antonio", "TX", 29.4241, -98.4936, 150),
        3: Customer(3, "San Diego", "CA", 32.7157, -117.1611, 120),
        4: Customer(4, "Dallas", "TX", 32.7767, -96.7970, 200),
        5: Customer(5, "San Jose", "CA", 37.3382, -121.8863, 180),
        6: Customer(6, "Austin", "TX", 30.2672, -97.7431, 130),
        7: Customer(7, "Jacksonville", "FL", 30.3322, -81.6557, 90),
        8: Customer(8, "Fort Worth", "TX", 32.7555, -97.3308, 110),
    }
    return customers


@pytest.fixture
def small_test_distance():
    """Fixture providing a distance matrix between warehouses and customers"""
    # Simple distance matrix for 5 warehouses and 8 customers
    # In a real scenario this would be calculated using haversine formula
    # or retrieved from a distance service
    distances = {}

    # Sample distances (km)
    distance_matrix = np.array(
        [
            [80, 2700, 4100, 2400, 4400, 2700, 1500, 2500],  # New York
            [4500, 2000, 180, 2000, 500, 2000, 3500, 2000],  # Los Angeles
            [1100, 1700, 3000, 1300, 2900, 1500, 1500, 1400],  # Chicago
            [2400, 300, 2100, 380, 2700, 270, 1300, 400],  # Houston
            [3600, 1200, 600, 1400, 1000, 1300, 2900, 1300],  # Phoenix
        ]
    )

    # Fill the dictionary with warehouse_id, customer_id pairs
    for w_id in range(1, 6):
        for c_id in range(1, 9):
            distances[(w_id, c_id)] = distance_matrix[w_id - 1, c_id - 1]

    return distances


@pytest.fixture
def capacitated_test_warehouses(small_test_warehouses):
    """Fixture providing warehouses with capacity constraints"""
    warehouses = small_test_warehouses

    # Add capacities
    warehouses[1].capacity = 300  # New York: can handle 300 units
    warehouses[2].capacity = 350  # Los Angeles: can handle 350 units
    warehouses[3].capacity = 400  # Chicago: can handle 400 units
    warehouses[4].capacity = 250  # Houston: can handle 250 units
    warehouses[5].capacity = 300  # Phoenix: can handle 300 units

    return warehouses


@pytest.fixture
def mock_solver_response():
    """Mock PuLP solver response for testing solution extraction"""

    class MockVar:
        def __init__(self, value):
            self.varValue = value

    class MockSolution:
        def __init__(self):
            self.status = 1  # Optimal
            self.objective = MockVar(100)

    return MockSolution()
