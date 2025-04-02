"""
Integration tests for the data mesh demo.
Tests that the domains can communicate with each other.
"""

import unittest
import time
import threading

from domain_alpha.controller import AlphaController
from domain_beta.controller import BetaController


class TestDomainIntegration(unittest.TestCase):
    """Test cases for domain integration."""

    def setUp(self):
        """Set up the test environment."""
        # Use different ports for testing to avoid conflicts
        self.alpha_controller = AlphaController("localhost", 9201)
        self.beta_controller = BetaController("localhost", 9202)

        # Start the controllers
        self.alpha_controller.start()
        self.beta_controller.start()

        # Wait for servers to start
        time.sleep(1)

        # Override the registry in the discovery module for testing
        import infra.discovery
        infra.discovery.REGISTRY["domain_alpha"] = ("localhost", 9201)
        infra.discovery.REGISTRY["domain_beta"] = ("localhost", 9202)

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'alpha_controller'):
            self.alpha_controller.stop()
        if hasattr(self, 'beta_controller'):
            self.beta_controller.stop()

        # Wait for servers to stop
        time.sleep(1)

    def test_beta_fetches_data_from_alpha(self):
        """Test that Beta can fetch data from Alpha."""
        # Beta fetches data from Alpha
        result = self.beta_controller.fetch_data_from_alpha()
        self.assertTrue(result)

        # Check that the data was stored correctly
        combined_data = self.beta_controller.data_product.get_combined_data()
        self.assertIn("AlphaDataProduct", combined_data)
        self.assertIn("Alpha data point", combined_data)

    def test_alpha_sends_message_to_beta(self):
        """Test that Alpha can send a message to Beta."""
        # Alpha sends a message to Beta
        response = self.alpha_controller.send_message_to_domain("domain_beta", "get_data")
        self.assertIsNotNone(response)
        self.assertIn("BetaDataProduct", response)

    def test_beta_fetches_specific_item_from_alpha(self):
        """Test that Beta can fetch a specific item from Alpha."""
        # Beta sends a message to Alpha
        response = self.beta_controller.send_message_to_domain("domain_alpha", "get_item:item2")
        self.assertEqual(response, "Alpha data point 2")

    def test_periodic_sync(self):
        """Test that the periodic sync works correctly."""
        # Start periodic sync with a short interval for testing
        self.beta_controller.start_periodic_sync(interval_seconds=1)

        # Wait for at least one sync to occur
        time.sleep(2)

        # Check that the data was stored correctly
        combined_data = self.beta_controller.data_product.get_combined_data()
        self.assertIn("AlphaDataProduct", combined_data)
        self.assertIn("Alpha data point", combined_data)


if __name__ == "__main__":
    unittest.main()