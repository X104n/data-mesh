"""
Data product module for the Beta domain.
Provides access to Beta domain's data and consumes data from Alpha domain.
"""


class BetaDataProduct:
    """Data product for the Beta domain."""

    def __init__(self):
        """Initialize the Beta data product."""
        self.product_name = "BetaDataProduct"
        self.version = "1.0"

        # Placeholder for Beta's own data
        self._data = {
            "analysis1": "Beta analysis of Alpha data",
            "analysis2": "Another Beta analysis",
        }

        # Placeholder for data fetched from Alpha
        self._alpha_data = None

    def get_data(self) -> str:
        """Get data from the Beta domain.

        Returns:
            A string containing data from the Beta domain
        """
        return f"Hello from {self.product_name}! Here's our analysis: {list(self._data.values())}"

    def get_analysis(self, analysis_id: str) -> str:
        """Get a specific analysis by ID.

        Args:
            analysis_id: The ID of the analysis to retrieve

        Returns:
            The requested analysis, or an error message if not found
        """
        if analysis_id in self._data:
            return self._data[analysis_id]
        return f"Analysis {analysis_id} not found"

    def store_alpha_data(self, data: str) -> None:
        """Store data received from the Alpha domain.

        Args:
            data: The data received from Alpha
        """
        self._alpha_data = data
        print(f"[{self.product_name}] Stored Alpha data: {data}")

    def get_combined_data(self) -> str:
        """Get a combination of Beta's data and the stored Alpha data.

        Returns:
            A string combining Beta's data with the stored Alpha data
        """
        if not self._alpha_data:
            return f"No Alpha data available. Beta data: {list(self._data.values())}"

        return f"Combined data from Beta and Alpha:\nBeta: {list(self._data.values())}\nAlpha: {self._alpha_data}"