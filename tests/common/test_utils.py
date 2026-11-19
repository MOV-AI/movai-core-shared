"""Unit tests for utils.py."""

from unittest.mock import patch

import pytest

from movai_core_shared.common import utils


@pytest.mark.parametrize(
    "fleet_role, expected",
    [
        ("manager", True),
        ("worker", False),
    ],
)
def test_is_manager(fleet_role, expected):
    with patch.object(utils, "FLEET_ROLE", fleet_role):
        assert utils.is_manager() is expected
