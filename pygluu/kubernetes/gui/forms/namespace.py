"""
pygluu.kubernetes.gui.forms.namespace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for namespace gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class NamespaceForm(FlaskForm):
    """
    Gluu namespace form

    Fields :
        gluu_namespace (string|required|default: gluu)
    """
    gluu_namespace = StringField("Gluu Namespace",
                                 default="gluu",
                                 validators=[InputRequired()])
