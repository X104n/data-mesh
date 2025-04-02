"""
Governance module for the data mesh demo.
Provides basic validation and logging functions for data exchange.
"""

from typing import Any


def verify_message(message: str) -> bool:
    """Verify that a message meets basic requirements.

    Args:
        message: The message to verify

    Returns:
        True if the message is valid, False otherwise

    Raises:
        ValueError: If the message is not a string or is empty
    """
    if not isinstance(message, str):
        raise ValueError("Message must be a string")

    if not message:
        raise ValueError("Message cannot be empty")

    print("Governance check passed for message")
    return True


def log_data_exchange(source_domain: str, target_domain: str, message_type: str) -> None:
    """Log a data exchange between domains.

    Args:
        source_domain: The domain sending the data
        target_domain: The domain receiving the data
        message_type: The type of message being exchanged
    """
    print(f"Data exchange: {source_domain} -> {target_domain}, type: {message_type}")