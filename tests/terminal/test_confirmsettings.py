def test_confirmsettings_confirm_params_accepted(monkeypatch, settings):
    from pygluu.kubernetes.terminal.confirmsettings import PromptConfirmSettings

    monkeypatch.setattr("click.confirm", lambda x: True)

    prompt = PromptConfirmSettings(settings)
    prompt.confirm_params()
    assert settings.get("CONFIRM_PARAMS") == "Y"


def test_confirmsettings_confirm_params_rejected(monkeypatch, settings):
    from pygluu.kubernetes.terminal.confirmsettings import PromptConfirmSettings

    monkeypatch.setattr("click.confirm", lambda x: False)
    # mock Prompt.prompt
    monkeypatch.setattr("pygluu.kubernetes.terminal.prompt.Prompt.prompt", lambda x: None)

    prompt = PromptConfirmSettings(settings)
    prompt.confirm_params()
    assert settings.get("CONFIRM_PARAMS") == "N"
