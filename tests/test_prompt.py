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
    monkeypatch.setattr("builtins.input", lambda x: given)

    # unset GLUU_VERSION in order to prompt user-input
    prompter.settings["GLUU_VERSION"] = ""
    prompter.prompt_version()
    assert prompter.settings["GLUU_VERSION"] == expected


def test_prompt_license_accepted(monkeypatch, prompter):
    monkeypatch.setattr("builtins.input", lambda x: "Y")

    # unset GLUU_VERSION in order to prompt user-input
    prompter.settings["ACCEPT_GLUU_LICENSE"] = ""
    prompter.prompt_license()
    assert prompter.settings["ACCEPT_GLUU_LICENSE"] == "Y"


@pytest.mark.parametrize("given", ["", "N"])
def test_prompt_license_rejected(monkeypatch, prompter, given):
    monkeypatch.setattr("builtins.input", lambda x: given)

    with pytest.raises(SystemExit):
        # unset GLUU_VERSION in order to prompt user-input
        prompter.settings["ACCEPT_GLUU_LICENSE"] = ""
        prompter.prompt_license()
