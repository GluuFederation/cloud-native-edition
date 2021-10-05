"""
pygluu.kubernetes.gui.forms.architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for setup of arch backend in gui installations.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired


class DeploymentArchForm(FlaskForm):
    """
    Deployment architecture form.

    Fields :
        deployment_arch (string|required|default: microk8s)
    """
    deployment_arch = RadioField(
        "Deployment Architecture",
        choices=[
            ("microk8s", "Microk8s"),
            ("minikube", "MiniKube"),
            ("eks", "Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)"),
            ("gke", "Google Cloud Engine - Google Kubernetes Engine (GKE)"),
            ("aks", "Microsoft Azure (AKS)"),
            ("do", "Digital Ocean "),
            ("local", "Manually provisioned Kubernetes cluster")],
        default="microk8s",
        validators=[DataRequired()])
