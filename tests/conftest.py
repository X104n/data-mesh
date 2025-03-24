import pytest
import os
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Setup the environment for testing"""
    # Create necessary directories
    Path('data').mkdir(exist_ok=True)
    Path('src/data').mkdir(exist_ok=True, parents=True)
    
    yield
    
    # Cleanup could go here if needed
