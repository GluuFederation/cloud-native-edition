"""
pygluu.kubernetes.gui.forms.gluugateway
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for gluu gateway gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, FormField, StringField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import PasswordInput
from .helpers import RequiredIfFieldEqualTo, password_requirement_check
from .postgres import PostgresForm


class GluuGatewayForm(FlaskForm):
    """
    Gluu Gateway Form

    Fields :
        install_gluu_gateway (string|required|default: N)
        postgres (form field form postgresForm)
        kong_namespace (string|required_if install_gluu_gateway = Y|default: gluu-gateway)
        gluu_gateway_ui_namesapce (string|required_if install_gluu_gateway = Y|default: gg-ui)
        kong_database (string|required_if install_gluu_gateway = Y|default: kong)
        kong_pg_user (string|required_if install_gluu_gateway = Y|default: konga)
        kong_pg_password (string|required_if install_gluu_gateway = Y|default: auto generated)
        kong_pg_password_confirmation (string|required_if install_gluu_gateway = Y|default: auto generated)
        gluu_gateway_ui_database (string|required_if install_gluu_gateway = Y|default: kong)
        gluu_gateway_ui_user (string|required_if install_gluu_gateway = Y|default: konga)
        gluu_gateway_ui_pg_password (string|required_if install_gluu_gateway = Y|default: auto generated)
        gluu_gateway_ui_pg_password_confirmation (string|required_if install_gluu_gateway = Y|default: auto generated)
    """
    install_gluu_gateway = RadioField("Install Gluu Gateway Database mode",
                                      choices=[("Y", "Yes"), ("N", "No")],
                                      default="N",
                                      validators=[DataRequired()])
    postgres = FormField(PostgresForm)
    kong_namespace = StringField(
        "Please enter a namespace for Gluu Gateway",
        default="gluu-gateway",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    gluu_gateway_ui_namespace = StringField(
        "Please enter a namespace for gluu gateway ui",
        default="gg-ui",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_database = StringField(
        "Please enter gluu-gateway postgres database name",
        default="kong",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_pg_user = StringField(
        "Please enter a user for gluu-gateway postgres database",
        default="konga",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_pg_password = StringField(
        "Kong Postgress Password",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    password_requirement_check()],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    kong_pg_password_confirm = StringField(
        "Kong Postgress Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    EqualTo('kong_pg_password_confirm',
                            message='Passwords do not match')])
    gluu_gateway_ui_database = StringField(
        "Please enter gluu-gateway-ui postgres database name",
        default="kong",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    gluu_gateway_ui_pg_user = StringField(
        "Please enter a user for gluu-gateway-ui postgres database",
        default="konga",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    gluu_gateway_ui_pg_password = StringField(
        "Gluu Gateway UI postgres password",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    password_requirement_check()],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    gluu_gateway_ui_pg_password_confirm = StringField(
        "Gluu Gateway UI postgres password confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    EqualTo('gluu_gateway_ui_pg_password',
                            message='Passwords do not match')])
