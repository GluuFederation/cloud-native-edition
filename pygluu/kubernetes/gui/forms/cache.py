"""
pygluu.kubernetes.gui.forms.cache
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for cache gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, FormField
from wtforms.validators import DataRequired
from .redis import RedisForm


class CacheTypeForm(FlaskForm):
    """
    Cache Type Form

    Fields :
        gluu_cache_type (string|required|default: NATIVE_PERSISTENCE)
    """
    gluu_cache_type = RadioField(
        "Cache Layer",
        choices=[("NATIVE_PERSISTENCE", "NATIVE_PERSISTENCE"),
                 ("IN_MEMORY", "IN_MEMORY"), ("REDIS", "REDIS")],
        default="NATIVE_PERSISTENCE",
        validators=[DataRequired()])
    redis = FormField(RedisForm)
