"""
pygluu.kubernetes.gui.forms.volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for volumes gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired, Optional, InputRequired
from pygluu.kubernetes.settings import SettingsHandler
from .helpers import app_volume_types, volume_types

settings = SettingsHandler()


class VolumeForm(FlaskForm):
    """
    Volume Form

    Fields:
        app_volume_type (string|required|default: based on deployment_arch selection see app_volume_types var)
        ldap_static_volume_id (string|optional)
        ldap_jackrabbit_volume (string|optional, became required for aks, eks and gke)
        ldap_storage_size (string|required|default: 4gi)
    """
    if settings.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
        ldap_volume = volume_types[settings.get("DEPLOYMENT_ARCH")]
        ldap_jackrabbit_volume_label = ldap_volume["label"]
        ldap_jackrabbit_volume_choices = ldap_volume["choices"]
        ldap_jackrabbit_volume_validators = [DataRequired()]
        ldap_jackrabbit_volume_render_kw = {}
    else:
        ldap_jackrabbit_volume_label = ""
        ldap_jackrabbit_volume_choices = []
        ldap_jackrabbit_volume_render_kw = {"disabled": "disabled"}
        ldap_jackrabbit_volume_validators = [Optional()]

    if settings.get("DEPLOYMENT_ARCH") and \
            settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
        volume_type = app_volume_types[settings.get("DEPLOYMENT_ARCH")]
    else:
        volume_type = app_volume_types["local"]

    app_volume_type = RadioField(volume_type["label"],
                                 choices=volume_type["choices"],
                                 default=volume_type["default"],
                                 validators=[DataRequired()],
                                 coerce=int)
    ldap_static_volume_id = StringField(
        "Please enter Persistent Disk Name or EBS Volume ID for LDAP",
        description="EBS Volume ID example: vol-049df61146c4d7901 "
                    "Persistent Disk Name example: "
                    "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd",
        render_kw={"disabled": "disabled"})
    ldap_static_disk_uri = StringField(
        "Please enter the disk uri for LDAP",
        description="DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                    "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk",
        render_kw={"disabled": "disabled"})
    ldap_jackrabbit_volume = RadioField(
        ldap_jackrabbit_volume_label,
        choices=ldap_jackrabbit_volume_choices,
        render_kw=ldap_jackrabbit_volume_render_kw,
        validators=ldap_jackrabbit_volume_validators)
    ldap_storage_size = StringField("Size of ldap volume storage",
                                    default="4Gi")
