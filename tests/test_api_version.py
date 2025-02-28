"""
Test the API version endpoint functionality.
"""

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.api.app import create_app


class TestAPIVersion(unittest.TestCase):
    """Test the API version endpoint."""

    def setUp(self):
        """Set up the test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_version_endpoint(self):
        """Test that the /version endpoint returns the correct version."""
        # Set the mock return value using patch in the test context
        test_version = "0.0.1"

        # Use context manager to patch the function at module level where FastAPI routes are defined
        with patch(
            'src.api.app.get_version',
            return_value=test_version
        ) as mock_get_version:
            # Make the request
            response = self.client.get("/version")

            # Check the response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"version": test_version})
            mock_get_version.assert_called_once()

    def test_version_in_api_info(self):
        """Test that the OpenAPI documentation includes the version."""
        # Make the request for OpenAPI schema
        response = self.client.get("/openapi.json")

        # Check the response contains version info
        self.assertEqual(response.status_code, 200)
        openapi_spec = response.json()
        self.assertIn("info", openapi_spec)
        self.assertIn("version", openapi_spec["info"])


if __name__ == '__main__':
    unittest.main()
