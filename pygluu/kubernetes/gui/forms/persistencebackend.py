"""
pygluu.kubernetes.gui.forms.persistencebackend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for persistence backend gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired


class PersistenceBackendForm(FlaskForm):
    """
    Persistence Backend Form.

    Fields :
        persistence_backend(string|required|default: ldap)
        hybrid_ldap_held_data(string|optional, available when persistence_backend is hybrid)
        sql_dialect(string|optional, available when persistence_backend is sql)
    """
    persistence_backend = RadioField(
        "Persistence layer",
        choices=[("ldap", "OpenDJ"),
                 ("couchbase", "Couchbase"),
                 ("sql", "SQL(MySQL/PostgreSQL)"),
                 ("spanner", "Spanner"),
                 ("hybrid", "Hybrid(OpenDJ + Couchbase)")],
        default="ldap",
        validators=[DataRequired()])
    hybrid_ldap_held_data = RadioField("Hybrid [OpenDJ + Couchbase]",
                                       choices=[("default", "Default"),
                                                ("user", "User"),
                                                ("site", "Site"),
                                                ("cache", "Cache"),
                                                ("token", "Token"),
                                                ("session", "Session")],
                                       default="default",
                                       render_kw={"disabled": "disabled"})
    sql_dialect = RadioField("SQL Dialect",
                                       choices=[("mysql", "MySQL"),
                                                ("pgsql", "PostgreSQL")],
                                       default="mysql",
                                       render_kw={"disabled": "disabled"})