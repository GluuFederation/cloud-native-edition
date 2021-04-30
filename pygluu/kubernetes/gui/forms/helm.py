"""
pygluu.kubernetes.gui.forms.helm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for helm gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Optional


class HelmForm(FlaskForm):
    gluu_helm_release_name = StringField("Please enter Gluu helm name",
                                         default="gluu",
                                         validators=[InputRequired()])
    nginx_ingress_release_name = StringField("Please enter nginx-ingress helm name",
                                             default="ningress",
                                             validators=[InputRequired()])
    nginx_ingress_namespace = StringField("Please enter nginx-ingress helm namespace",
                                          default="ingress-nginx",
                                          validators=[InputRequired()])
