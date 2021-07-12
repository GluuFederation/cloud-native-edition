"""
pygluu.kubernetes.gui.forms.configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for configuration gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import re

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, MultipleFileField
from wtforms.widgets import PasswordInput
from wtforms.validators import InputRequired, Email, EqualTo, \
    Optional, ValidationError
from .helpers import password_requirement_check, RequiredIfFieldEqualTo

class ConfigurationForm(FlaskForm):
    """
    Config Form

    Fields:
        gluu_fqdn (string|required|default: demoexample.gluu.org)
        country_code (string|required|default: US)
        state (string|required|default: TX)
        city (string|required|default: Austin)
        email (string|required|default: support@gluu.org)
        org_name (string|required|default: Gluu)
        admin_pw (string|required|default: auto generated)
        admin_pw_confirm (string|required, equal to admin_pw)
        ldap_pw (string|optional, required for hybrid and ldap backend)
        ldap_pw_confirm (string|equal to ldap_pw)
        is_gluu_fqdn_registered (string|optional)
        migration_enabled(string|optional)
        migration_files(file|optional)
        migration_data_format(string|optional)
    TODO: find a better way to override ldap_pw validators
    """
    gluu_fqdn = StringField("Hostname",
                            default="demoexample.gluu.org",
                            validators=[InputRequired()])
    country_code = StringField("Country Code",
                               default="US",
                               validators=[InputRequired()])
    state = StringField("State",
                        default="TX",
                        validators=[InputRequired()])
    city = StringField("City",
                       default="Austin",
                       validators=[InputRequired()])
    email = StringField("Email",
                        default="support@gluu.org",
                        validators=[Email()])
    org_name = StringField("Organization",
                           default="Gluu",
                           validators=[InputRequired()])
    admin_pw = StringField(
        "oxTrust Password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(),
                    password_requirement_check()],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    admin_pw_confirm = StringField(
        "oxTrust Password Confirm",
        widget=PasswordInput(hide_value=False),
        validators=[EqualTo("admin_pw")])
    ldap_pw = StringField(
        "LDAP Password",
        widget=PasswordInput(hide_value=False),
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    ldap_pw_confirm = StringField("LDAP Password Confirm",
                                  widget=PasswordInput(hide_value=False),
                                  validators=[EqualTo("ldap_pw")])
    is_gluu_fqdn_registered = RadioField(
        "Are you using a globally resolvable FQDN",
        choices=[("Y", "Yes"), ("N", "No")],
        description="You can mount your FQDN certification and key by placing "
                    "them inside gluu.crt and gluu.key respectivley "
                    "at the same location pygluu-kubernetes.pyz is at.",
        render_kw={"disabled": "disabled"})

    migration_enabled = RadioField(
        "Are you migrating from the Gluu community edition (VM base)",
        choices=[("Y", "Yes"), ("N", "No")],
        render_kw={"disabled": "disabled"})

    migration_files = MultipleFileField(
        "CE migration files",
        description="Upload the CE migration files.",
        validators=[RequiredIfFieldEqualTo("migration_enabled", "Y")])

    migration_data_format = RadioField(
        "Migration data-format depending on persistence backend.",
        choices=[("ldif", "OpenDJ"),
                 ("couchbase+json", "Couchbase"),
                 ("postgresql+json", "PostgreSQL"),
                 ("mysql+json", "MySQL"),
                 ("spanner+avro", "Spanner")],
        default="ldap",
        validators=[RequiredIfFieldEqualTo("migration_enabled", "Y")])

    def validate_gluu_fqdn(self, field):
        """
        FQDN validation format
        """
        regex_bool = re.match(
            r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$',
            self.gluu_fqdn.data)

        if not regex_bool:
            raise ValidationError("Input not FQDN structured. Please enter a FQDN with the format demoexample.gluu.org")
