import pytest


@pytest.mark.parametrize("given, expected", [
    (True, "Y"),
    (False, "N"),
])
def test_helpers_confirm_yesno(monkeypatch, given, expected):
    from pygluu.kubernetes.terminal.helpers import confirm_yesno

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert confirm_yesno("Random question") == expected
