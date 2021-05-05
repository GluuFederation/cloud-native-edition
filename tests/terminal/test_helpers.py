import pytest
import click
from pygluu.kubernetes.terminal.helpers import gather_ip
import ipaddress

@pytest.mark.parametrize("given, expected", [
    (True, True),
    (False, False),
])
def test_helpers_confirm_yesno(monkeypatch, given, expected):

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert click.confirm("Random question") == expected
