"""
pygluu.kubernetes.gui.forms.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for postgres gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField
from wtforms.validators import InputRequired, DataRequired


class PostgresForm(FlaskForm):
    """
    Postgres Form

    Fields :
    install_postgres (string|required|default: Y)
    postgres_namespace (string|required|default: postgres)
    postgres_url (string|required|default: postgresql.postgres.svc.cluster.local  )
    """
    install_postgres = RadioField(
        "Install Postgres", choices=[("Y", "Yes"), ("N", "No")], default="Y",
        description="For the following prompt if N is placed "
                    "Postgres is assumed to be"
                    " installed or remotely provisioned. "
                    "Install Bitnami Postgres chart?",
        validators=[DataRequired()])
    postgres_namespace = StringField(
        "Please enter a namespace for postgres",
        default="postgres",
        validators=[InputRequired()])
    postgres_url = StringField(
        "Please enter  postgres (remote or local) URL base name. "
        "If postgres is to be installed",
        default="postgresql.postgres.svc.cluster.local",
        validators=[InputRequired()])
