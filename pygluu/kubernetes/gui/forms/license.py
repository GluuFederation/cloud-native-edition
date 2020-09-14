"""
pygluu.kubernetes.gui.license
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's input for gui license form

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms.validators import DataRequired


class LicenseForm(FlaskForm):
    """
    License form,
    form to accept Apache 2.0 lisence

    Fields :
        accept_gluu_license (string|required)
    """
    accept_gluu_license = BooleanField(
        "I accept the Gluu license stated above",
        validators=[DataRequired(message="License has not been accepted")])
