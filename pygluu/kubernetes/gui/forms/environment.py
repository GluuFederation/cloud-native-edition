"""
pygluu.kubernetes.gui.environment
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for environment gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired, InputRequired, IPAddress, \
    Email
from .helpers import RequiredIfFieldEqualTo


class EnvironmentForm(FlaskForm):
    """
    Setting Form.

    Fields :
        test_environment (string|required|default: N)
        node_ssh_key (string|optional|default: ~/.ssh/id_rsa)
        host_ext_ip (string|required|default: 127.0.0.1)
        use_lb_type (string|optional|default: clb)
        use_arn (string|optional|default: N)
        arn_aws_iam (string|optional, available when deployment_arch is eks)
        gmail_account(string|optional, available when deployment_arch is gke)
    """
    test_environment = RadioField("Is this test a test environment?",
                                  choices=[("Y", "Yes"), ("N", "No")],
                                  default="N",
                                  validators=[DataRequired()])
    node_ssh_key = StringField(
        "Please enter the ssh key path if exists to "
        "login into the nodes created[~/.ssh/id_rsa]",
        default="~/.ssh/id_rsa")
    host_ext_ip = StringField("Please input the host's external IP address",
                              default="127.0.0.1",
                              validators=[InputRequired(), IPAddress()])
    aws_lb_type = RadioField(
        "AWS Loadbalancer type",
        choices=[("clb", "Classic Load Balancer (CLB)"),
                 ("nlb", "Network Load Balancer (NLB - Alpha) -- Static IP"),
                 ("alb", "Application Load Balancer (ALB - Alpha) DEV_ONLY")],
        default="clb",
        validators=[DataRequired()])
    use_arn = RadioField(
        "Are you terminating SSL traffic at LB and using certificate from AWS",
        choices=[("Y", "Yes"), ("N", "No")],
        default="N")
    arn_aws_iam = StringField(
        "Enter aws-load-balancer-ssl-cert arn quoted "
        "('arn:aws:acm:us-west-2:XXXXXXXX: certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX')",
        validators=[RequiredIfFieldEqualTo('use_arn', 'Y')])
    gmail_account = StringField(
        "Please enter valid email for Google Cloud account",
        validators=[Email()])
