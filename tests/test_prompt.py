import contextlib
import os

import pytest


@pytest.fixture
def prompter():
    from pygluu.kubernetes.prompt import Prompt

    prompt = Prompt(accept_license=True, version="4.2.0_dev")

    yield prompt

    # cleanup
    for file_ in ["settings.json", "gluu_versions.json"]:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(file_)


@pytest.mark.parametrize("given, expected", [
    (True, "Y"),
    (False, "N"),
])
def test_confirm_yesno(monkeypatch, given, expected):
    from pygluu.kubernetes.prompt import confirm_yesno

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert confirm_yesno("Random question") == expected


def test_prompt_license_no_prompt(prompter):
    prompter.prompt_license()
    assert prompter.settings["ACCEPT_GLUU_LICENSE"] == "Y"


def test_prompt_version_no_prompt(prompter):
    prompter.prompt_version()
    assert prompter.settings["GLUU_VERSION"] == "4.2.0_dev"


@pytest.mark.parametrize("given, expected", [
    ("", "0"),
    ("4.2.0_dev", "4.2.0_dev"),
])
def test_prompt_version(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    # unset GLUU_VERSION in order to prompt user-input
    prompter.settings["GLUU_VERSION"] = ""
    prompter.prompt_version()
    assert prompter.settings["GLUU_VERSION"] == expected


def test_prompt_license_accepted(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x: True)

    # unset GLUU_VERSION in order to prompt user-input
    prompter.settings["ACCEPT_GLUU_LICENSE"] = ""
    prompter.prompt_license()
    assert prompter.settings["ACCEPT_GLUU_LICENSE"] == "Y"


def test_prompt_license_rejected(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x: False)

    with pytest.raises(SystemExit):
        # unset GLUU_VERSION in order to prompt user-input
        prompter.settings["ACCEPT_GLUU_LICENSE"] = ""
        prompter.prompt_license()


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
def test_prompt_arch(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given)
    prompter.prompt_arch()
    assert prompter.settings["DEPLOYMENT_ARCH"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),
    ("my-ns", "my-ns"),
])
def test_prompt_gluu_namespace(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.prompt_gluu_namespace()
    assert prompter.settings["GLUU_NAMESPACE"] == expected
