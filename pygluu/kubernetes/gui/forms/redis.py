"""
pygluu.kubernetes.gui.forms.redis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for redis gui form.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, IntegerField, StringField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms.widgets import PasswordInput
from .helpers import RequiredIfFieldEqualTo


class RedisForm(FlaskForm):
    """
    Redis Form

    Fields:
        redis_type (string|optional|default: CLUSTER)
        install_redis (string|required|default: Y)
        redis_namespace (string|required_if install_redis is Y| default: gluu-redis-cluster)
        redis_pw (string|required_if install_redis is Y)
        redis_pw_confirm (string|required_if install_redis is Y|equal_to redis_pw)
        redis_url (string|optional|default : redis-cluster.gluu-redis-cluster.svc.cluster.local:6379)
    """
    redis_type = RadioField("Please select redis Type",
                            choices=[("STANDALONE", "STANDALONE"),
                                     ("CLUSTER", "CLUSTER")],
                            default="CLUSTER")
    install_redis = RadioField(
        "Install Redis", choices=[("Y", "Yes"), ("N", "No")], default="Y",
        description="For the following prompt if placed [N] "
                    "the Redis is assumed to be "
                    "installed or remotely provisioned",
        validators=[DataRequired()])
    redis_namespace = StringField(
        "Please enter a namespace for Redis cluster",
        default="gluu-redis-cluster",
        validators=[RequiredIfFieldEqualTo("install_redis", "Y")])
    redis_pw = StringField(
        "Redis Password",
        widget=PasswordInput(hide_value=False),
        validators=[])
    redis_pw_confirm = StringField(
        "Redis Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[
                    EqualTo('redis_pw', message='Passwords do not match')])
    redis_url = StringField(
        "Please enter redis URL. If you are deploying redis",
        default="redis-cluster.gluu-redis-cluster.svc.cluster.local:6379",
        description="Redis URL can be : redis-cluster.gluu-redis-cluster.svc.cluster.local:6379 "
        "in a redis deployment Redis URL using AWS ElastiCach "
        "[Configuration Endpoint]: clustercfg.testing-redis.icrbdv.euc1.cache.amazonaws.com:6379")
