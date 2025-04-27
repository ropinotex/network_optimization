import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from netopt import get_city_coords


class TestGetCityCoords:
    """Tests for the get_city_coords function"""

    @patch("requests.get")
    def test_successful_coordinates_lookup(self, mock_get):
        """Test successful lookup of city coordinates"""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "lat": "40.7128",
                "lon": "-74.0060",
                "display_name": "New York, New York, United States",
            }
        ]
        mock_get.return_value = mock_response

        # Call the function
        lat, lon = get_city_coords("New York")

        # Check that the request was made with the expected parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["q"] == "New York"

        # Check that the coordinates were correctly parsed
        assert lat == 40.7128
        assert lon == -74.0060

    @patch("requests.get")
    def test_empty_response(self, mock_get):
        """Test handling of empty API response"""
        # Set up mock response with empty results
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Call the function with a nonexistent city
        lat, lon = get_city_coords("NonexistentCity12345")

        # Check that None values are returned
        assert lat is None
        assert lon is None

    @patch("requests.get")
    def test_exception_handling(self, mock_get):
        """Test handling of exceptions during API call"""
        # Set up mock to raise exception
        mock_get.side_effect = Exception("API error")

        # Call the function
        lat, lon = get_city_coords("New York")

        # Check that None values are returned on error
        assert lat is None
        assert lon is None
