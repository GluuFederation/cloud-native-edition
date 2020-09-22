"""
pygluu.kubernetes.gui.forms.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for postgres gui forms.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired


class PostgresForm(FlaskForm):
    """
    Postgres Form

    Fields :
    postgres_namespace (string|required|default: postgres)
    postgres_replicas (integer|required|default: 3)
    postgres_url (string|required|default: postgres.postgres.svc.cluster.local  )
    """
    postgres_namespace = StringField(
        "Please enter a namespace for postgres",
        default="postgres",
        validators=[InputRequired()])
    postgres_replicas = IntegerField(
        "Please enter number of replicas for postgres",
        default=3,
        validators=[InputRequired()])
    postgres_url = StringField(
        "Please enter  postgres (remote or local) URL base name. "
        "If postgres is to be installed",
        default="postgres.postgres.svc.cluster.local",
        validators=[InputRequired()])
