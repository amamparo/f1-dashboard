#!/usr/bin/env python
"""Tests for `esm_fullstack_challenge` package."""
import pytest

import esm_fullstack_challenge


@pytest.fixture
def dummy_fixture():
    """Dummy fixture to avoid import error."""
    return 'REPLACE ME!'


def test_has_metadata():
    """Test if package has metadata."""
    assert hasattr(esm_fullstack_challenge, '__author__')
    assert hasattr(esm_fullstack_challenge, '__email__')
    assert hasattr(esm_fullstack_challenge, '__version__')
