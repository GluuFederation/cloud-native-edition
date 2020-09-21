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
    """
    persistence_backend = RadioField(
        "Persistence layer",
        choices=[("ldap", "WrenDS"),
                 ("couchbase", "Couchbase"),
                 ("hybrid", "Hybrid(WrenDS + Couchbase)")],
        default="ldap",
        validators=[DataRequired()])
    hybrid_ldap_held_data = RadioField("Hybrid [WrendDS + Couchbase]",
                                       choices=[("default", "Default"),
                                                ("user", "User"),
                                                ("site", "Site"),
                                                ("cache", "Cache"),
                                                ("token", "Token"),
                                                ("session", "Session")],
                                       default="default",
                                       render_kw={"disabled": "disabled"})
