"""
pygluu.kubernetes.gui.forms.sql
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for postgres gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, FormField
from wtforms.validators import InputRequired, DataRequired, EqualTo
from wtforms.widgets import PasswordInput

from .helpers import password_requirement_check, RequiredIfFieldEqualTo


class SqlForm(FlaskForm):
    """
    SQL Form

    Fields :
    install_sql (string|required|default: Y)
    sql_namespace (string|required|default: postgres)
    sql_url (string|required|default: gluu.sql.svc.cluster.local  )
    sql_user (string|required: default gluu)
    sql_password (string|required: default auto generated)
    sql_password_confirmation (string|required equal to jackrabbit_pg_password)
    sql_database (string|required)
    """
    install_sql = RadioField(
        "Install SQL Dialect. This will install Postgres or MySQL depending on the dialect chosen previously.", choices=[("Y", "Yes"), ("N", "No")], default="Y",
        description="For the following prompt if N is placed "
                    "MySQL is assumed to be"
                    " installed or remotely provisioned. "
                    "Install Bitnami MySQL chart?",
        validators=[DataRequired()])
    sql_namespace = StringField(
        "Please enter a namespace for the SQL server",
        default="mysql",
        validators=[RequiredIfFieldEqualTo("install_sql", "Y")])
    sql_url = StringField(
        "Please enter  SQL (remote or local) URL base name. ",
        default="gluu-mysql.sql.svc.cluster.local")
    sql_user = StringField("Please enter a user for Gluu SQL database",
                                     default="gluu",
                                     validators=[RequiredIfFieldEqualTo("install_sql", "Y")])
    sql_password = StringField("Gluu SQL User Password",
                                         widget=PasswordInput(hide_value=False),
                                         validators=[RequiredIfFieldEqualTo("install_sql", "Y"),
                                                     password_requirement_check()])
    sql_password_confirmation = StringField(
        "Gluu SQL User Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_sql", "Y"),
                    EqualTo("sql_password")])
    sql_database = StringField("Please enter Gluu SQL database name",
                                      default="gluu")