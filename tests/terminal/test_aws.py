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

    settings.set("USE_ARN", "N")
    settings.set("ARN_AWS_IAM", "Y")
    PromptAws(settings).prompt_aws_lb()
    assert settings.get("AWS_LB_TYPE") == expected


def test_aws_arn(monkeypatch, settings):
    from pygluu.kubernetes.terminal.aws import PromptAws

    monkeypatch.setattr("click.confirm", lambda x: True)

    fake_arn = "arn:aws:acm:random"
    monkeypatch.setattr("click.prompt", lambda x: fake_arn)
    settings.set("VPC_CIDR", "192.168.0.0/16")
    settings.set("AWS_LB_TYPE", "alb")
    PromptAws(settings).prompt_aws_lb()
    assert settings.get("USE_ARN") == "Y"
    assert settings.get("ARN_AWS_IAM") == fake_arn
