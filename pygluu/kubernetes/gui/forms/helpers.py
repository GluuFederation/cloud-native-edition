"""
pygluu.kubernetes.gui.forms.helpers

This module contains helpers classes, functions and variable that being use by the forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import re
from wtforms.validators import DataRequired, Optional, ValidationError


app_volume_types = {
    "eks": {

        "label": "Amazon Web Services - Elastic Kubernetes Service (Amazon EKS) MultiAZ - Supported",
        "choices": [(6, "volumes on host"),
                    (7, "EBS volumes dynamically provisioned"),
                    (8, "EBS volumes statically provisioned")],
        "default": 6
    },
    "gke": {
        "label": "Google Cloud Engine - Google Kubernetes Engine",
        "choices": [(11, "volumes on host"),
                    (12, "Persistent Disk  dynamically provisioned"),
                    (13, "Persistent Disk  statically provisioned")],
        "default": 12
    },
    "aks": {
        "label": "Microsoft Azure",
        "choices": [(16, "volumes on host"),
                    (17, "Persistent Disk  dynamically provisioned"),
                    (18, "Persistent Disk  statically provisioned")],
        "default": 17
    },
    "do": {
        "label": "Digital Ocean",
        "choices": [(21, "volumes on host"),
                    (22, "Persistent Disk  dynamically provisioned"),
                    (23, "Persistent Disk  statically provisioned")],
        "default": 22
    },
    "local": {
        "label": "Local Development",
        "choices": [(26, "OpenEBS Local PV Hostpath")],
        "default": 26
    }
}

volume_types = {
    "aks": {
        "label": "Azure Options",
        "choices": [("Standard_LRS", "Standard_LRS"),
                    ("Premium_LRS", "Premium_LRS"),
                    ("StandardSSD_LRS", "StandardSSD_LRS"),
                    ("UltraSSD_LRS", "UltraSSD_LRS")],
    },
    "eks": {
        "label": "AWS EKS Options",
        "choices": [("gp2", "gp2"),
                    ("io1", "io1"),
                    ("st1", "st1"),
                    ("sc1", "sc1")],
    },
    "gke": {
        "label": "GCE GKE Options",
        "choices": [("pd-standard", "pd-standard"),
                    ("pd-ssd", "pd-ssd")],
    }
}


def password_requirement_check():
    """
    Password Requirement validation,
    password required contain at least one digit,
    uppercase letter, lower case and symbol
    """
    message = "Password does not meet requirements. "\
              "The password must contain one digit, one uppercase "\
              "letter, one lower case letter and one symbol"

    def _password_requirement_check(form, field):
        regex_bool = re.match(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z0-9\S]{6,}$',
            field.data)
        if not regex_bool:
            raise ValidationError(message)

    return _password_requirement_check


class RequiredIfFieldEqualTo(DataRequired):
    """
    A validator which makes a field optional if
    another field has a desired value
    """

    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        super(RequiredIfFieldEqualTo, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if other_field.data == self.value:
            super(RequiredIfFieldEqualTo, self).__call__(form, field)
        Optional()(form, field)


class RequiredIfFieldIn(DataRequired):
    """
    A validator which makes a field optional if
    another field has a desired value
    """

    def __init__(self, other_field_name, values, *args, **kwargs):
        self.other_field_name = other_field_name
        self.values = values
        super(RequiredIfFieldIn, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if type(self.values) is not list:
            raise Exception('object values is not an array')

        if other_field.data in self.values:
            super(RequiredIfFieldIn, self).__call__(form, field)
        Optional()(form, field)
