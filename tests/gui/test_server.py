import pytest


@pytest.mark.parametrize("given, expected", [
    ([], "0.0.0.0"),
    (["-H", "127.0.0.1"], "127.0.0.1"),
    (["--host", "localhost"], "localhost"),
])
def test_parse_args_host(given, expected):
    from pygluu.kubernetes.gui.server import parse_args

    args = parse_args(given)
    assert args.host == expected


@pytest.mark.parametrize("given, expected", [
    ([], 5000),
    (["-p", "8000"], 8000),
    (["--port", "3000"], 3000),
])
def test_parse_args_port(given, expected):
    from pygluu.kubernetes.gui.server import parse_args

    args = parse_args(given)
    assert args.port == expected


@pytest.mark.parametrize("given, expected", [
    ([], False),
    (["-d"], True),
    (["--debug"], True),
])
def test_parse_args_debug(given, expected):
    from pygluu.kubernetes.gui.server import parse_args

    args = parse_args(given)
    assert args.debug is expected
