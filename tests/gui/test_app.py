import pytest


@pytest.fixture
def mock_kube_load(monkeypatch):
    def mock_load(*args):
        return

    monkeypatch.setattr("pygluu.kubernetes.kubeapi.load_kubernetes_config", mock_load)
    yield


@pytest.mark.parametrize("given, expected", [
    ([], "0.0.0.0"),
    (["-H", "127.0.0.1"], "127.0.0.1"),
    (["--host", "localhost"], "localhost"),
])
def test_parse_args_host(mock_kube_load, given, expected):
    from pygluu.kubernetes.gui.app import parse_args

    args = parse_args(given)
    assert args.host == expected


@pytest.mark.parametrize("given, expected", [
    ([], 5000),
    (["-p", "8000"], 8000),
    (["--port", "3000"], 3000),
])
def test_parse_args_port(mock_kube_load, given, expected):
    from pygluu.kubernetes.gui.app import parse_args

    args = parse_args(given)
    assert args.port == expected


@pytest.mark.parametrize("given, expected", [
    ([], False),
    (["-d"], True),
    (["--debug"], True),
])
def test_parse_args_debug(mock_kube_load, given, expected):
    from pygluu.kubernetes.gui.app import parse_args

    args = parse_args(given)
    assert args.debug is expected
