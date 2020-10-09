"""
pygluu.kubernetes.gui.forms.volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for volumes gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField


class VolumeForm(FlaskForm):
    """
    Volume Form

    Fields:
        app_volume_type (string|required|default: based on deployment_arch selection see app_volume_types var)
        ldap_static_volume_id (string|optional)
        ldap_jackrabbit_volume (string|optional, became required for aks, eks and gke)
        ldap_storage_size (string|required|default: 4gi)
    Notes :
        app_volume_type and ldap_jackrabbit_volume is a dynamic fields, field data will be
        set when the form is loaded
    """

    app_volume_type = RadioField("", choices=[], default="", coerce=int)
    ldap_static_volume_id = StringField(
        "Please enter Persistent Disk Name or EBS Volume ID for LDAP",
        description="EBS Volume ID example: vol-049df61146c4d7901 "
                    "Persistent Disk Name example: "
                    "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd")
    ldap_static_disk_uri = StringField(
        "Please enter the disk uri for LDAP",
        description="DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                    "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")
    ldap_jackrabbit_volume = RadioField("", choices=[])
    ldap_storage_size = StringField("Size of ldap volume storage",
                                    default="4Gi")
