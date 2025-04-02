"""
Unit tests for the Alpha domain.
"""

import unittest
from domain_alpha.data_product import AlphaDataProduct
from domain_alpha.controller import AlphaController


class TestAlphaDataProduct(unittest.TestCase):
    """Test cases for the Alpha data product."""

    def setUp(self):
        """Set up the test environment."""
        self.data_product = AlphaDataProduct()

    def test_get_data(self):
        """Test that get_data returns a string with expected content."""
        data = self.data_product.get_data()
        self.assertIsInstance(data, str)
        self.assertIn("AlphaDataProduct", data)
        self.assertIn("Alpha data point", data)

    def test_get_item(self):
        """Test that get_item returns the expected item."""
        item = self.data_product.get_item("item1")
        self.assertEqual(item, "Alpha data point 1")

    def test_get_nonexistent_item(self):
        """Test that get_item returns an error message for nonexistent items."""
        item = self.data_product.get_item("nonexistent")
        self.assertIn("not found", item)


class TestAlphaController(unittest.TestCase):
    """Test cases for the Alpha controller."""

    def setUp(self):
        """Set up the test environment."""
        # Use a different port for testing to avoid conflicts
        self.controller = AlphaController("localhost", 9101)

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'controller'):
            self.controller.stop()

    def test_handle_message_get_data(self):
        """Test that handle_message correctly handles the get_data command."""
        response = self.controller.handle_message("get_data", ("localhost", 0))
        self.assertIn("AlphaDataProduct", response)
        self.assertIn("Alpha data point", response)

    def test_handle_message_get_item(self):
        """Test that handle_message correctly handles the get_item command."""
        response = self.controller.handle_message("get_item:item1", ("localhost", 0))
        self.assertEqual(response, "Alpha data point 1")

    def test_handle_message_unknown_command(self):
        """Test that handle_message correctly handles unknown commands."""
        response = self.controller.handle_message("unknown_command", ("localhost", 0))
        self.assertIn("Unknown command", response)


if __name__ == "__main__":
    unittest.main()