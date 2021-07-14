"""
pygluu.kubernetes.gui.forms.optionalservices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for optional services gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, StringField
from wtforms.validators import DataRequired
from .helpers import RequiredIfFieldEqualTo


class OptionalServiceForm(FlaskForm):
    """
    Optional Service Form

    Fields :
        enable_cache_refresh (string|required|default: N)
        enable_oxauth_key_rotate (string|required|default: N)
        oxauth_keys_life (string|required|default: N)
        enable_oxpassport (string|required|default: N)
        enable_oxshibboleth (string|required|default: N)
        enable_casa (string|required|default: N)
        enable_fido2 (string|required|default: N)
        enable_scim (string|required|default: N)
        enable_oxd (string|required|default: N)
        oxd_application_keystore_cn (string|required_if enable_oxd = Y|default: oxd-server)
        oxd_admin_keystore_cn (string|required_if enable_oxd = Y|default: oxd-server)
        enable_oxtrust_api (string|required|default: N)
        enable_oxtrust_test_mode (string|required|default: N)
    """
    enable_cache_refresh = RadioField("Deploy Cr-Rotate",
                                      choices=[("Y", "Yes"), ("N", "No")],
                                      default="N",
                                      validators=[DataRequired()])
    enable_oxauth_key_rotate = RadioField("Deploy Key-Rotation",
                                          choices=[("Y", "Yes"), ("N", "No")],
                                          default="N",
                                          validators=[DataRequired()])
    oxauth_keys_life = IntegerField(
        "oxAuth keys life in hours",
        default=48,
        validators=[RequiredIfFieldEqualTo("enable_oxauth_key_rotate", "Y")])
    enable_oxpassport = RadioField("Deploy Passport",
                                   choices=[("Y", "Yes"), ("N", "No")],
                                   default="N",
                                   validators=[DataRequired()])
    enable_oxshibboleth = RadioField("Deploy Shibboleth SAML IDP",
                                     choices=[("Y", "Yes"), ("N", "No")],
                                     default="N",
                                     validators=[DataRequired()])
    enable_casa = RadioField("Deploy Casa",
                             choices=[("Y", "Yes"), ("N", "No")],
                             default="N",
                             validators=[DataRequired()])
    enable_fido2 = RadioField("Deploy Fido2",
                              choices=[("Y", "Yes"), ("N", "No")],
                              default="N",
                              validators=[DataRequired()])
    enable_scim = RadioField("Deploy scim",
                             choices=[("Y", "Yes"), ("N", "No")],
                             default="N",
                             validators=[DataRequired()])
    enable_oxd = RadioField("Deploy oxd server",
                            choices=[("Y", "Yes"), ("N", "No")],
                            default="N",
                            validators=[DataRequired()])
    oxd_application_keystore_cn = StringField(
        "oxd server application keystore name",
        default="oxd-server",
        validators=[RequiredIfFieldEqualTo("enable_oxd", "Y")])
    oxd_admin_keystore_cn = StringField(
        "oxd server admin keystore name",
        default="oxd-server",
        validators=[RequiredIfFieldEqualTo("enable_oxd", "Y")])

    enable_oxtrust_api = RadioField("Enable oxTrust API",
                                    choices=[("Y", "Yes"), ("N", "No")],
                                    default="N",
                                    validators=[DataRequired()])
    enable_oxtrust_test_mode = RadioField("Enable oxTrust Test Mode",
                                          choices=[("Y", "Yes"), ("N", "No")],
                                          default="N",
                                          validators=[DataRequired()])
