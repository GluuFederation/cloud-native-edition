"""
pygluu.kubernetes.gui.forms.jackrabbit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for jackrabbit gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

from flask_wtf import FlaskForm

from wtforms import RadioField, StringField, FormField
from wtforms.validators import DataRequired, URL, InputRequired, EqualTo
from wtforms.widgets import PasswordInput

from .helpers import password_requirement_check, RequiredIfFieldEqualTo
from .postgres import PostgresForm


class JackrabbitForm(FlaskForm):
    """
    Jackrabbit Form

    Fields
    ------
        install_jackrabbit (string|required) : default Y
        jackrabbit_url (string|required_if install_jackrabbit = N): default http://jackrabbit:8080
        jackrabbit_admin_id (string|required): default admin
        jackrabbit_admin_password (string|required): default auto generated
        jackrabbit_admin_password_confirmation (string|required|equal to jackrabbit_admin_password)
        jackrabbit_cluster (string|required): default Y
        jackrabbit_pg_user (string|required_if jackrabbit_cluster = Y): default jackrabbit
        jackrabbit_pg_password (string|required_if jackrabbit_cluster = Y): default auto generated
        jackrabbit_pg_password_confirmation (string|required_if jackrabbit_cluster = Y| equal to jackrabbit_pg_password)
        jackrabbit_pg_database (string|required_if jackrabbit_cluster = Y)
        jackrabbit_storage_size (string|required_if install_jackrabbit = Y)
        postgres (form field from PostgresFrom)
    """
    install_jackrabbit = RadioField(
        "Install Jackrabbit content repository",
        choices=[("Y", "Yes"), ("N", "No")],
        default="Y",
        validators=[DataRequired()])
    jackrabbit_url = StringField(
        "Please enter jackrabbit url",
        default="http://jackrabbit:8080",
        validators=[RequiredIfFieldEqualTo("install_jackrabbit", "N"),
                    URL(require_tld=False, message="Url format is wrong")])
    jackrabbit_admin_id = StringField(
        "Please enter jackrabbit admin user",
        default="admin",
        validators=[InputRequired()])
    jackrabbit_admin_password = StringField(
        "Jackrabbit Admin Password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(),
                    password_requirement_check()])
    jackrabbit_admin_password_confirmation = StringField(
        "Jackrabbit Admin Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(),
                    EqualTo("jackrabbit_admin_password")])
    jackrabbit_cluster = RadioField(
        "Enable Jackrabbit in cluster mode[beta] Recommended in production",
        choices=[("Y", "Yes"), ("N", "No")],
        default="Y",
        validators=[DataRequired()])
    jackrabbit_pg_user = StringField("Please enter a user for jackrabbit postgres database",
                                     default="jackrabbit",
                                     validators=[RequiredIfFieldEqualTo("jackrabbit_cluster", "Y")])
    jackrabbit_pg_password = StringField("Jackrabbit PG Password",
                                         widget=PasswordInput(hide_value=False),
                                         validators=[RequiredIfFieldEqualTo("jackrabbit_cluster", "Y"),
                                                     password_requirement_check()])
    jackrabbit_pg_password_confirmation = StringField(
        "Jackrabbit PG Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("jackrabbit_cluster", "Y"),
                    EqualTo("jackrabbit_pg_password")])
    jackrabbit_database = StringField("Please enter jackrabbit postgres database name",
                                      default="jackrabbit")
    jackrabbit_storage_size = StringField(
        "Size of Jackrabbit content repository volume storage",
        default="4Gi",
        validators=[RequiredIfFieldEqualTo("install_jackrabbit", "Y")])
    postgres = FormField(PostgresForm)
