import pytest


@pytest.mark.parametrize("given, expected", [
    (True, "Y"),
    (False, "N"),
])
def test_helpers_confirm_yesno(monkeypatch, given, expected):

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert click.confirm("Random question") == expected
