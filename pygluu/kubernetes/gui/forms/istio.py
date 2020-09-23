"""
pygluu.kubernetes.gui.forms.istio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for istio gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired, Optional
from .helpers import RequiredIfFieldEqualTo


class IstioForm(FlaskForm):
    """
    Istio Form

    Fields:
        use_istio_ingress
        use_istio
        istio_system_namespace
        lb_add
    """

    use_istio_ingress = RadioField("[Alpha] Would you like to use Istio Ingress with Gluu ?",
                                   choices=[("Y", "Yes"), ("N", "No")],
                                   validators=[Optional()])
    use_istio = RadioField(
        "[Alpha] Would you like to use Istio with Gluu ?",
        choices=[("Y", "Yes"), ("N", "No")],
        validators=[DataRequired()],
        description="Istio will auto inject side cars into all pods in Gluus namespace chosen. "
                    "The label istio-injection=enabled will be added to the namespace Gluu will be installed in "
                    "if the namespace does not exist. If it does please run "
                    "kubectl label namespace <namespace> istio-injection=enabled")
    istio_system_namespace = StringField("Istio namespace",
                                         default="istio-system",
                                         validators=[RequiredIfFieldEqualTo("use_istio", "Y")])
    lb_add = StringField("Istio loadbalancer address (eks) or "
                         "ip (gke, aks, digital ocean, local)",
                         default="",
                         validators=[RequiredIfFieldEqualTo("use_istio_ingress", "Y")])
