from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import InputRequired, Optional


class ReplicasForm(FlaskForm):
    """
    Replicas Form

    Fields:
        auth_server_replicas (integer|required|default: 1)
        fido2_replicas (integer|optional|default: 1)
        scim_replicas (integer|optional|default: 1)
        oxtrust_replicas (integer|optional|default: 1)
        ldap_replicas (integer|optional|default: 1)
        oxshibboleth_replicas (integer|optional|default: 1)
        oxpassport_replicas (integer|optional|default: 1)
        client_api_server_replicas (integer|optional|default: 1)
        casa_replicas (integer|optional|default: 1)
        radius_replicas (integer|optional|default: 1)
    """
    auth_server_replicas = IntegerField("Number of Auth-Server replicas", default=1, validators=[InputRequired()])
    fido2_replicas = IntegerField("Number of fido2 replicas", default=1, validators=[Optional()])
    scim_replicas = IntegerField("Number of scim replicas", default=1, validators=[Optional()])
    oxtrust_replicas = IntegerField("Number of oxTrust replicas", default=1, validators=[Optional()])
    ldap_replicas = IntegerField("Number of LDAP replicas", default=1, validators=[Optional()])
    oxshibboleth_replicas = IntegerField("Number of oxShibboleth replicas",
                                         default=1,
                                         validators=[Optional()])
    oxpassport_replicas = IntegerField("Number of oxPassport replicas",
                                       default=1,
                                       validators=[Optional()])
    client_api_server_replicas = IntegerField("Number of client-api replicas",
                                       default=1,
                                       validators=[Optional()])
    casa_replicas = IntegerField("Number of Casa replicas", default=1, validators=[Optional()])
    radius_replicas = IntegerField("Number of Radius replicas", default=1, validators=[Optional()])
