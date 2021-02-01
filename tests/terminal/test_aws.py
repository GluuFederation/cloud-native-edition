import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "clb"),  # default
    (1, "clb"),
    (2, "nlb"),
    (3, "alb"),
])
def test_aws_loadbalancer(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.aws import PromptAws

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("CN_USE_ARN", "N")
    PromptAws(settings).prompt_aws_lb()
    assert settings.get("installer-settings.aws.lbType") == expected


def test_aws_arn(monkeypatch, settings):
    from pygluu.kubernetes.terminal.aws import PromptAws

    monkeypatch.setattr("click.confirm", lambda x: True)

    fake_arn = "arn:aws:acm:random"
    monkeypatch.setattr("click.prompt", lambda x: fake_arn)
    settings.set("CN_VPC_CIDR", "192.168.0.0/16")
    settings.set("installer-settings.aws.lbType", "alb")
    PromptAws(settings).prompt_aws_lb()
    assert settings.get("CN_USE_ARN")
    assert settings.get("CN_ARN_AWS_IAM") == fake_arn
