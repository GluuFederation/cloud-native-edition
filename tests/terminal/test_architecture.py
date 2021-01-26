import pytest


@pytest.mark.parametrize("given, expected", [
    (1, "microk8s"),
    (2, "minikube"),
    (3, "eks"),
    (4, "gke"),
    (5, "aks"),
    (6, "do"),
    (7, "local"),
    ("random", "microk8s"),
])
def test_arch(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.architecture import PromptArch

    monkeypatch.setattr("click.prompt", lambda x, default: given)

    settings.set("CN_DEPLOYMENT_ARCH", "")
    prompt = PromptArch(settings)
    prompt.prompt_arch()
    assert settings.get("CN_DEPLOYMENT_ARCH") == expected
