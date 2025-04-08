"""
Unit tests for the generalized domain implementation.
"""

import unittest
import time
import threading

from domain import DataProduct, DomainController


class TestDataProduct(unittest.TestCase):
    """Test cases for the generalized DataProduct class."""

    def setUp(self):
        """Set up the test environment."""
        initial_data = {
            "item1": "Test data point 1",
            "item2": "Test data point 2",
        }
        self.data_product = DataProduct("test_domain", initial_data)

    def test_get_data(self):
        """Test that get_data returns a string with expected content."""
        data = self.data_product.get_data()
        self.assertIsInstance(data, str)
        self.assertIn("TestDomainDataProduct", data)
        self.assertIn("Test data point", data)

    def test_get_item(self):
        """Test that get_item returns the expected item."""
        item = self.data_product.get_item("item1")
        self.assertEqual(item, "Test data point 1")

    def test_get_nonexistent_item(self):
        """Test that get_item returns an error message for nonexistent items."""
        item = self.data_product.get_item("nonexistent")
        self.assertIn("not found", item)
        
    def test_store_external_data(self):
        """Test storing external data from another domain."""
        self.data_product.store_external_data("external_domain", "External data")
        combined_data = self.data_product.get_combined_data()
        self.assertIn("External data", combined_data)


class TestDomainController(unittest.TestCase):
    """Test cases for the DomainController class."""

    def setUp(self):
        """Set up the test environment."""
        self.domain_a = DomainController(
            domain_name="domain_a",
            host="localhost",
            port=9901,
            initial_data={"item1": "Domain A data"}
        )
        
        self.domain_b = DomainController(
            domain_name="domain_b",
            host="localhost",
            port=9902,
            initial_data={"item1": "Domain B data"}
        )
        
        # Start the domains
        self.domain_a.start()
        self.domain_b.start()
        
        # Register domains with each other
        self.domain_a.register_domain("domain_b", "localhost", 9902)
        self.domain_b.register_domain("domain_a", "localhost", 9901)
        
        # Give servers time to start
        time.sleep(1)

    def tearDown(self):
        """Clean up after tests."""
        self.domain_a.stop()
        self.domain_b.stop()
        
        # Give servers time to stop
        time.sleep(1)

    def test_send_message(self):
        """Test sending a message between domains."""
        response = self.domain_a.send_message("domain_b", "localhost", 9902, "get_data")
        self.assertIsNotNone(response)
        self.assertIn("Domain B data", response)

    def test_fetch_data(self):
        """Test fetching data from another domain."""
        result = self.domain_b.fetch_data_from_domain("domain_a", "localhost", 9901)
        self.assertTrue(result)
        
        # Check the combined data
        combined_data = self.domain_b.data_product.get_combined_data()
        self.assertIn("Domain A data", combined_data)
        self.assertIn("Domain B data", combined_data)

    def test_periodic_sync(self):
        """Test the periodic sync functionality."""
        # Start sync with a short interval
        self.domain_a.start_periodic_sync("domain_b", interval_seconds=1)
        
        # Wait for a sync to happen
        time.sleep(2)
        
        # Check combined data
        combined_data = self.domain_a.data_product.get_combined_data()
        self.assertIn("Domain B data", combined_data)


if __name__ == "__main__":
    unittest.main()