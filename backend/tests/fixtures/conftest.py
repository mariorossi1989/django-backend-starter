"""Shared pytest fixtures for all tests.

Define common fixtures used across multiple test files here.
"""

import pytest


@pytest.fixture
def sample_data():
    """Example shared fixture.

    Returns sample data for testing.
    """
    return {
        "id": 1,
        "name": "Test Item",
        "active": True,
    }
