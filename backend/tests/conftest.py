"""Shared pytest configuration and fixtures.

This file is automatically loaded by pytest and provides fixtures
available to all tests.
"""

import pytest


@pytest.fixture
def sample_fixture():
    """Example fixture.

    Replace or extend with your actual fixtures.
    """
    return {"key": "value"}
