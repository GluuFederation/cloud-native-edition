#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, \
    BooleanField, PasswordField, FormField, FileField, MultipleFileField
from wtforms.validators import DataRequired, InputRequired, \
    EqualTo, URL, IPAddress, Email, Required, ValidationError, \
    Optional
from wtforms.widgets import PasswordInput
from pygluu.kubernetes.common import get_supported_versions
from pygluu.kubernetes.settingdb import SettingDB
settings = SettingDB()

app_volume_types = {
    "eks": {

        "label": "Amazon Web Services - Elastic Kubernetes Service (Amazon EKS) MultiAZ - Supported",
        "choices": [(6, "volumes on host"),
                    (7, "EBS volumes dynamically provisioned"),
                    (8, "EBS volumes statically provisioned")],
        "default": 6
    },
    "gke": {
        "label": "Google Cloud Engine - Google Kubernetes Engine",
        "choices": [(11, "volumes on host"),
                    (12, "Persistent Disk  dynamically provisioned"),
                    (13, "Persistent Disk  statically provisioned")],
        "default": 12
    },
    "aks": {
        "label": "Microsoft Azure",
        "choices": [(16, "volumes on host"),
                    (17, "Persistent Disk  dynamically provisioned"),
                    (18, "Persistent Disk  statically provisioned")],
        "default": 17
    },
    "do": {
        "label": "Digital Ocean",
        "choices": [(21, "volumes on host"),
                    (22, "Persistent Disk  dynamically provisioned"),
                    (23, "Persistent Disk  statically provisioned")],
        "default": 22
    },
    "local": {
        "label": "Local Development",
        "choices": [(26, "OpenEBS Local PV Hostpath")],
        "default": 26
    }
}

volume_types = {
    "aks": {
        "label": "Azure Options",
        "choices": [("Standard_LRS", "Standard_LRS"),
                    ("Premium_LRS", "Premium_LRS"),
                    ("StandardSSD_LRS", "StandardSSD_LRS"),
                    ("UltraSSD_LRS", "UltraSSD_LRS")],
    },
    "eks": {
        "label": "AWS EKS Options",
        "choices": [("gp2", "gp2"),
                    ("io1", "io1"),
                    ("st1", "st1"),
                    ("sc1", "sc1")],
    },
    "gke": {
        "label": "GCE GKE Options",
        "choices": [("pd-standard", "pd-standard"),
                    ("pd-ssd", "pd-ssd")],
    }
}


def password_requirement_check(form, field):
    regex_bool = re.match(
        '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z0-9\S]{6,}$',
        field.data)
    if not regex_bool:
        raise ValidationError(
            "Password does not meet requirements. "
            "The password must contain one digit, one uppercase "
            "letter, one lower case letter and one symbol")


class RequiredIfFieldEqualTo(Required):
    """
    a validator which makes a field optional if
    another field has a desired value
    """

    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        super(RequiredIfFieldEqualTo, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if other_field.data == self.value:
            super(RequiredIfFieldEqualTo, self).__call__(form, field)
        Optional()(form, field)


class LicenseForm(FlaskForm):
    accept_gluu_license = BooleanField(
        "I accept the Gluu license stated above",
        validators=[DataRequired(message="License has not been accepted")])


class GluuVersionForm(FlaskForm):
    versions, version_number = get_supported_versions()
    supported_versions = []

    for k, v in versions.items():
        supported_versions.append((version_number, k))

    gluu_version = RadioField(
        "Currently supported versions",
        choices=supported_versions,
        validators=[DataRequired(message="Please select version")])


class DeploymentArchForm(FlaskForm):
    deployment_arch = RadioField(
        "Deployment Architecture",
        choices=[
            ("microk8s", "Microk8s"),
            ("minikube", "MiniKube"),
            ("eks", "Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)"),
            ("gke", "Google Cloud Engine - Google Kubernetes Engine (GKE)"),
            ("aks", "Microsoft Azure (AKS)"),
            ("do", "Digital Ocean [BETA]"),
            ("local", "Manually provisioned Kubernetes cluster")],
        default="microk8s",
        validators=[DataRequired()])


class GluuNamespaceForm(FlaskForm):
    gluu_namespace = StringField("Gluu Namespace",
                                 default="gluu",
                                 validators=[InputRequired()])


class OptionalServiceForm(FlaskForm):
    enable_cache_refresh = RadioField("Deploy Cr-Rotate",
                                      choices=[("Y", "Yes"), ("N", "No")],
                                      default="N",
                                      validators=[DataRequired()])
    enable_oxauth_key_rotate = RadioField("Deploy Key-Rotation",
                                          choices=[("Y", "Yes"), ("N", "No")],
                                          default="N",
                                          validators=[DataRequired()])
    oxauth_keys_life = IntegerField(
        "oxAuth keys life in hours",
        default=48,
        validators=[RequiredIfFieldEqualTo("enable_oxauth_key_rotate", "Y")])
    enable_radius = RadioField("Deploy Radius?",
                               choices=[("Y", "Yes"), ("N", "No")],
                               default="N",
                               validators=[DataRequired()])
    enable_oxpassport = RadioField("Deploy Passport",
                                   choices=[("Y", "Yes"), ("N", "No")],
                                   default="N",
                                   validators=[DataRequired()])
    enable_oxshibboleth = RadioField("Deploy Shibboleth SAML IDP",
                                     choices=[("Y", "Yes"), ("N", "No")],
                                     default="N",
                                     validators=[DataRequired()])
    enable_casa = RadioField("Deploy Casa",
                             choices=[("Y", "Yes"), ("N", "No")],
                             default="N",
                             validators=[DataRequired()])
    enable_fido2 = RadioField("Deploy Fido2",
                              choices=[("Y", "Yes"), ("N", "No")],
                              default="N",
                              validators=[DataRequired()])
    enable_scim = RadioField("Deploy scim",
                             choices=[("Y", "Yes"), ("N", "No")],
                             default="N",
                             validators=[DataRequired()])
    enable_oxd = RadioField("Deploy oxd server",
                            choices=[("Y", "Yes"), ("N", "No")],
                            default="N",
                            validators=[DataRequired()])
    oxd_application_keystore_cn = StringField(
        "oxd server application keystore name",
        default="oxd-server",
        validators=[RequiredIfFieldEqualTo("enable_oxd", "Y")])
    oxd_admin_keystore_cn = StringField(
        "oxd server admin keystore name",
        default="oxd-server",
        validators=[RequiredIfFieldEqualTo("enable_oxd", "Y")])

    enable_oxtrust_api = RadioField("Enable oxTrust API",
                                    choices=[("Y", "Yes"), ("N", "No")],
                                    default="N",
                                    validators=[DataRequired()])
    enable_oxtrust_test_mode = RadioField("Enable oxTrust Test Mode",
                                          choices=[("Y", "Yes"), ("N", "No")],
                                          default="N",
                                          validators=[DataRequired()])


class GluuGatewayForm(FlaskForm):
    install_gluu_gateway = RadioField("Install Gluu Gateway Database mode",
                                      choices=[("Y", "Yes"), ("N", "No")],
                                      default="N",
                                      validators=[DataRequired()])
    postgres_namespace = StringField(
        "Please enter number of replicas for postgres",
        default="postgres",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    postgres_replicas = IntegerField(
        "Please enter a namespace for postgres",
        default=3,
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    postgres_url = StringField(
        "Please enter  postgres (remote or local) URL base name. "
        "If postgres is to be installed",
        default="postgres.postgres.svc.cluster.local",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_namespace = StringField(
        "Please enter a namespace for Gluu Gateway",
        default="gluu-gateway",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    gluu_gateway_ui_namespace = StringField(
        "Please enter a namespace for gluu gateway ui",
        default="gg-ui",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_database = StringField(
        "Please enter gluu-gateway postgres database name",
        default="kong",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_pg_user = StringField(
        "Please enter a user for gluu-gateway postgres database",
        default="konga",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    kong_pg_password = StringField(
        "Kong Postgress Password",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    password_requirement_check],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    kong_pg_password_confirm = StringField(
        "Kong Postgress Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    EqualTo('kong_pg_password_confirm',
                            message='Passwords do not match')])
    gluu_gateway_ui_database = StringField(
        "Please enter gluu-gateway-ui postgres database name",
        default="kong",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    gluu_gateway_ui_pg_user = StringField(
        "Please enter a user for gluu-gateway-ui postgres database",
        default="konga",
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y")])
    gluu_gateway_ui_pg_password = StringField(
        "Gluu Gateway UI postgres password",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    password_requirement_check],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    gluu_gateway_ui_pg_password_confirm = StringField(
        "Gluu Gateway UI postgres password confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_gluu_gateway", "Y"),
                    EqualTo('gluu_gateway_ui_pg_password',
                            message='Passwords do not match')])


class JackrabbitForm(FlaskForm):
    install_jackrabbit = RadioField("Install Jackrabbit",
                                    choices=[("Y", "Yes"), ("N", "No")],
                                    default="Y",
                                    validators=[DataRequired()])
    jackrabbit_url = StringField(
        "Please enter jackrabbit url",
        default="http://jackrabbit:8080",
        validators=[RequiredIfFieldEqualTo("install_jackrabbit", "N"),
                    URL(require_tld=False, message="Url format is wrong")])
    jackrabbit_user = StringField(
        "Please enter jackrabbit user",
        default="admin",
        validators=[RequiredIfFieldEqualTo("install_jackrabbit", "N")])
    jackrabbit_storage_size = StringField(
        "Size of Jackrabbit content repository volume storage",
        default="4Gi",
        validators=[RequiredIfFieldEqualTo("install_jackrabbit", "Y")])


class SettingForm(FlaskForm):
    test_environment = RadioField("Is this test a test environment?",
                                  choices=[("Y", "Yes"), ("N", "No")],
                                  default="N",
                                  validators=[DataRequired()])
    node_ssh_key = StringField(
        "Please enter the ssh key path if exists to "
        "login into the nodes created[~/.ssh/id_rsa]",
        default="~/.ssh/id_rsa")
    host_ext_ip = StringField("Please input the host's external IP address",
                              default="127.0.0.1",
                              validators=[InputRequired(), IPAddress()])
    aws_lb_type = RadioField(
        "AWS Loadbalancer type",
        choices=[("clb", "Classic Load Balancer (CLB)"),
                 ("nlb", "Network Load Balancer (NLB - Alpha) -- Static IP"),
                 ("alb", "Application Load Balancer (ALB - Alpha) DEV_ONLY")],
        default="clb",
        validators=[DataRequired()])
    use_arn = RadioField(
        "Are you terminating SSL traffic at LB and using certificate from AWS",
        choices=[("Y", "Yes"), ("N", "No")],
        default="N")
    arn_aws_iam = StringField(
        "Enter aws-load-balancer-ssl-cert arn quoted "
        "('arn:aws:acm:us-west-2:XXXXXXXX: certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX')",
        render_kw={"disabled": "disabled"})
    gmail_account = StringField(
        "Please enter valid email for Google Cloud account",
        validators=[Email()])
    persistence_backend = RadioField(
        "Persistence layer",
        choices=[("ldap", "WrenDS"),
                 ("couchbase", "Couchbase [Testing Phase]"),
                 ("hybrid", "Hybrid(WrenDS + Couchbase)[Testing Phase]")],
        default="ldap",
        validators=[DataRequired()])
    hybrid_ldap_held_data = RadioField("Hybrid [WrendDS + Couchbase]",
                                       choices=[("default", "Default"),
                                                ("user", "User"),
                                                ("site", "Site"),
                                                ("cache", "Cache"),
                                                ("token", "Token")],
                                       default="default",
                                       render_kw={"disabled": "disabled"})


class VolumeTypeForm(FlaskForm):

    if settings.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
        ldap_volume = volume_types[settings.get("DEPLOYMENT_ARCH")]
        ldap_jackrabbit_volume_label = ldap_volume["label"]
        ldap_jackrabbit_volume_choices = ldap_volume["choices"]
        ldap_jackrabbit_volume_validators = [DataRequired()]
        ldap_jackrabbit_volume_render_kw = {}
    else:
        ldap_jackrabbit_volume_label = ""
        ldap_jackrabbit_volume_choices = []
        ldap_jackrabbit_volume_render_kw = {"disabled": "disabled"}
        ldap_jackrabbit_volume_validators = [Optional()]

    if settings.get("DEPLOYMENT_ARCH") and \
            settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
        volume_type = app_volume_types[settings.get("DEPLOYMENT_ARCH")]
    else:
        volume_type = app_volume_types["local"]

    app_volume_type = RadioField(volume_type["label"],
                                 choices=volume_type["choices"],
                                 default=volume_type["default"],
                                 validators=[DataRequired()],
                                 coerce=int)
    ldap_static_volume_id = StringField(
        "Please enter Persistent Disk Name or EBS Volume ID for LDAP",
        description="EBS Volume ID example: vol-049df61146c4d7901",
        render_kw={"disabled": "disabled"})
    ldap_static_disk_uri = StringField(
        "Please enter the disk uri for LDAP",
        description="DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                    "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk",
        render_kw={"disabled": "disabled"})
    ldap_jackrabbit_volume = RadioField(
        ldap_jackrabbit_volume_label,
        choices=ldap_jackrabbit_volume_choices,
        render_kw=ldap_jackrabbit_volume_render_kw,
        validators=ldap_jackrabbit_volume_validators)


class CouchbaseMultiClusterForm(FlaskForm):
    deploy_multi_cluster = RadioField(
        "Is this a multi-cloud/region setup?",
        choices=[("Y", "Yes"), ("N", "No")],
        description="If you are planning for a multi-cloud/region "
                    "setup and this is the first cluster answer N "
                    "You will answer Y for the second and more cluster setup")


class RedisForm(FlaskForm):
    redis_type = RadioField("Please select redis Type",
                            choices=[("STANDALONE", "STANDALONE"),
                                     ("CLUSTER", "CLUSTER")],
                            default="CLUSTER")
    install_redis = RadioField(
        "Install Redis", choices=[("Y", "Yes"), ("N", "No")], default="Y",
        description="For the following prompt if placed [N] "
                    "the Redis is assumed to be "
                    "installed or remotely provisioned",
        validators=[RequiredIfFieldEqualTo("install_redis", "Y")])
    redis_master_nodes = IntegerField(
        "The number of master node. Minimum is 3",
        default=3,
        validators=[RequiredIfFieldEqualTo("install_redis", "Y")],
        render_kw={"min": 3})
    redis_nodes_per_master = IntegerField(
        "The number of nodes per master node",
        default=2,
        validators=[RequiredIfFieldEqualTo("install_redis", "Y")])
    redis_namespace = StringField(
        "Please enter a namespace for Redis cluster",
        default="gluu-redis-cluster",
        validators=[RequiredIfFieldEqualTo("install_redis", "Y")])
    redis_pw = StringField(
        "Redis Password",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_redis", "N")])
    redis_pw_confirm = StringField(
        "Redis Password Confirmation",
        widget=PasswordInput(hide_value=False),
        validators=[RequiredIfFieldEqualTo("install_redis", "N"),
                    EqualTo('redis_pw', message='Passwords do not match')])
    redis_url = StringField(
        "Please enter redis URL. If you are deploying redis",
        default="redis-cluster.gluu-redis-cluster.svc.cluster.local:6379",
        description="Redis URL can be : redis-cluster.gluu-redis-cluster.svc.cluster.local:6379 "
        "in a redis deployment Redis URL using AWS ElastiCach "
        "[Configuration Endpoint]: clustercfg.testing-redis.icrbdv.euc1.cache.amazonaws.com:6379")

    def validate_master_nodes(form, field):
        if field.data < 3:
            raise ValidationError("minimum number of master node is 3")


class CacheTypeForm(FlaskForm):
    gluu_cache_type = RadioField(
        "Cache Layer",
        choices=[("NATIVE_PERSISTENCE", "NATIVE_PERSISTENCE"),
                 ("IN_MEMORY", "IN_MEMORY"), ("REDIS", "REDIS")],
        default="NATIVE_PERSISTENCE",
        validators=[DataRequired()])
    redis = FormField(RedisForm)


class CouchbaseForm(FlaskForm):
    install_couchbase = RadioField(
        "Install Couchbase", choices=[("Y", "Yes"), ("N", "No")],
        description="For the following prompt if placed [N] the couchbase "
                    "is assumed to be installed or remotely provisioned",
        validators=[DataRequired()])
    couchbase_crt = FileField(
        "Couchbase certificate",
        description="Place the Couchbase certificate authority certificate in a file called couchbase.crt "
                    "This can also be found in your couchbase UI Security > Root Certificate",
        validators=[RequiredIfFieldEqualTo("install_couchbase", "N")])
    couchbase_cluster_file_override = RadioField(
        "Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml",
        choices=[("Y", "Yes"), ("N", "No")], validators=[DataRequired()])
    couchbase_cluster_files = MultipleFileField(
        "Couchbase override files",
        description="Please upload the override files under the name "
                    "couchbase-cluster.yaml, couchbase-buckets.yaml, "
                    "and couchbase-ephemeral-buckets.yaml",
        validators=[RequiredIfFieldEqualTo("couchbase_cluster_file_override", "Y")])
    couchbase_use_low_resources = RadioField(
        "Setup CB nodes using low resources for demo purposes",
        choices=[("Y", "Yes"), ("N", "No")])
    couchbase_namespace = StringField(
        "Please enter a namespace for CB objects",
        default="cbns", validators=[InputRequired()])
    couchbase_cluster_name = StringField("Please enter a cluster name",
                                         default="cbgluu",
                                         validators=[InputRequired()])
    couchbase_url = StringField(
        "Please enter  couchbase (remote or local) URL base name",
        default="cbgluu.cbns.svc.cluster.local",
        validators=[InputRequired()])
    couchbase_user = StringField("Please enter couchbase username",
                                 default="admin",
                                 validators=[InputRequired()])
    couchbase_password = StringField(
        "Couchbase password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(), password_requirement_check],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    couchbase_password_confirmation = PasswordField(
        "Couchbase password confirm",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(), EqualTo("couchbase_password")])
    couchbase_cn = StringField("Enter Couchbase certificate common name.",
                               default="Couchbase CA")


class CouchbaseCalculatorForm(FlaskForm):
    number_of_expected_users = IntegerField(
        "Please enter the number of expected users", default=1000000)
    using_resource_owner_password_cred_grant_flow = RadioField(
        "Will you be using the resource owner password credential grant flow",
        choices=[("Y", "Yes"), ("N", "No")],
        default="Y")
    using_code_flow = RadioField("Will you be using the code flow",
                                 choices=[("Y", "Yes"), ("N", "No")],
                                 default="Y")
    using_scim_flow = RadioField("Will you be using the SCIM flow",
                                 choices=[("Y", "Yes"), ("N", "No")],
                                 default="Y")
    expected_transaction_per_sec = StringField(
        "Expected transactions per second",
        default=2000)
    couchbase_data_nodes = StringField(
        "Please enter the number of data nodes. (auto-calculated)",
        default="")
    couchbase_index_nodes = StringField(
        "Please enter the number of index nodes. (auto-calculated)",
        default="")
    couchbase_query_nodes = StringField(
        "Please enter the number of query nodes. (auto-calculated)",
        default="")
    couchbase_search_eventing_analytics_nodes = StringField(
        "Please enter the number of search,eventing and analytics nodes. (auto-calculated)",
        default="")
    couchbase_general_storage = StringField(
        "Please enter the general storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_data_storage = StringField(
        "Please enter the data storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_index_storage = StringField(
        "Please enter the index node storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_query_storage = StringField(
        "Please enter the data storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_analytics_storage = StringField(
        "Please enter the analytics node storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_volume_type = RadioField("Please select the volume type.",
                                       choices=[],
                                       validators=[Optional()])


class CouchbaseBackupForm(FlaskForm):
    couchbase_incr_backup_schedule = StringField(
        "Please input couchbase backup cron job schedule for incremental backups. "
        "This will run backup job every 30 mins by default.",
        default="*/30 * * * *")
    couchbase_full_backup_schedule = StringField(
        "Please input couchbase backup cron job schedule for full backups. ",
        default="0 2 * * 6")
    couchbase_backup_retention_time = StringField(
        "Please enter the time period in which to retain existing backups. "
        "Older backups outside this time frame are deleted",
        default="168h")
    couchbase_backup_storage_size = StringField(
        "Size of couchbase backup volume storage",
        default="20Gi")


class LdapBackupForm(FlaskForm):
    ldap_backup_schedule = StringField(
        "Please input ldap backup cron job schedule. "
        "This will run backup job every 30 mins by default.",
        default="*/30 * * * *")


class ConfigForm(FlaskForm):
    gluu_fqdn = StringField("Hostname",
                            default="demoexample.gluu.org",
                            validators=[InputRequired()])
    country_code = StringField("Country Code",
                               default="US",
                               validators=[InputRequired()])
    state = StringField("State",
                        default="TX",
                        validators=[InputRequired()])
    city = StringField("City",
                       default="Austin",
                       validators=[InputRequired()])
    email = StringField("Email",
                        default="support@gluu.org",
                        validators=[Email()])
    org_name = StringField("Organization",
                           default="Gluu",
                           validators=[InputRequired()])
    admin_pw = StringField(
        "oxTrust Password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(),
                    password_requirement_check],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    admin_pw_confirm = StringField(
        "oxTrust Password Confirm",
        widget=PasswordInput(hide_value=False),
        validators=[EqualTo("admin_pw")])
    ldap_pw = StringField(
        "LDAP Password",
        widget=PasswordInput(hide_value=False),
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    ldap_pw_confirm = StringField("LDAP Password Confirm",
                                  widget=PasswordInput(hide_value=False),
                                  validators=[EqualTo("ldap_pw")])
    is_gluu_fqdn_registered = RadioField(
        "Are you using a globally resolvable FQDN",
        choices=[("Y", "Yes"), ("N", "No")],
        description="You can mount your FQDN certification and key by placing "
                    "them inside gluu.crt and gluu.key respectivley "
                    "at the same location pygluu-kuberentest.pyz is at.",
        render_kw={"disabled": "disabled"})

    # override ldap_pw validators
    if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
        ldap_pw.validators = [InputRequired(), password_requirement_check]
    else:
        ldap_pw.validators = [Optional()]
        ldap_pw.render_kw = {"disabled": "disabled"}

    def validate_gluu_fqdn(form, field):
        regex_bool = re.match(
            '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$',
            # noqa: W605
            form.gluu_fqdn.data)

        if not regex_bool:
            raise ValidationError("Input not FQDN structred. Please enter a FQDN with the format demoexample.gluu.org")


class ImageNameTagForm(FlaskForm):
    # TODO: find a way to generate dynamic fields

    edit_image_names_tags = RadioField(
        "Would you like to manually edit the image source/name and tag",
        choices=[("Y", "Yes"), ("N", "No")],
        validators=[DataRequired()])
    casa_image_name = StringField(
        "Casa image name",
        default=settings.get("CASA_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    casa_image_tag = StringField(
        "Casa image tag",
        default=settings.get("CASA_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    config_image_name = StringField(
        "Config image name",
        default=settings.get("CONFIG_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    config_image_tag = StringField(
        "Config image tag",
        default=settings.get("CONFIG_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cache_refresh_rotate_image_name = StringField(
        "CR-rotate image name",
        default=settings.get("CACHE_REFRESH_ROTATE_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cache_refresh_rotate_image_tag = StringField(
        "CR-rotate image tag",
        default=settings.get("CACHE_REFRESH_ROTATE_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cert_manager_image_name = StringField(
        "Key rotate image name",
        default=settings.get("CERT_MANAGER_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cert_manager_image_tag = StringField(
        "Key rotate image tag",
        default=settings.get("CERT_MANAGER_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    ldap_image_name = StringField(
        "WrenDS image name",
        default=settings.get("LDAP_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    ldap_image_tag = StringField(
        "WrenDS image tag",
        default=settings.get("LDAP_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    jackrabbit_image_name = StringField(
        "Jackrabbit image name",
        default=settings.get("JACKRABBIT_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    jackrabbit_image_tag = StringField(
        "Jackrabbit image tag",
        default=settings.get("JACKRABBIT_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxauth_image_name = StringField(
        "Oxauth image name",
        default=settings.get("OXAUTH_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxauth_image_tag = StringField(
        "Oxauth image tag",
        default=settings.get("OXAUTH_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxd_image_name = StringField(
        "Oxd Server image name",
        default=settings.get("OXD_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxd_image_tag = StringField(
        "Oxd Server image tag",
        default=settings.get("OXD_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxpassport_image_name = StringField(
        "oxPassport image name",
        default=settings.get("OXPASSPORT_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxpassport_image_tag = StringField(
        "oxPassport image tag",
        default=settings.get("OXPASSPORT_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxshibboleth_image_name = StringField(
        "oxShibboleth image name",
        default=settings.get("OXSHIBBOLETH_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxshibboleth_image_tag = StringField(
        "oxShibboleth image tag",
        default=settings.get("OXSHIBBOLETH_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxtrust_image_name = StringField(
        "oxTrust image name",
        default=settings.get("OXTRUST_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxtrust_image_tag = StringField(
        "oxTrust image tag",
        default=settings.get("OXTRUST_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    persistence_image_name = StringField(
        "Persistence image name",
        default=settings.get("PERSISTENCE_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    persistence_image_tag = StringField(
        "Persistence image tag",
        default=settings.get("PERSISTENCE_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    radius_image_name = StringField(
        "Radius image name",
        default=settings.get("RADIUS_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    radius_image_tag = StringField(
        "Radius image tag",
        default=settings.get("RADIUS_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_image_name = StringField(
        "Gluu-Gateway image name",
        default=settings.get("GLUU_GATEWAY_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_image_tag = StringField(
        "Gluu-Gateway image tag",
        default=settings.get("GLUU_GATEWAY_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_ui_image_name = StringField(
        "Gluu-Gateway-UI image name",
        default=settings.get("GLUU_GATEWAY_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_ui_image_tag = StringField(
        "Gluu-Gateway-UI image tag",
        default=settings.get("GLUU_GATEWAY_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])


class ReplicasForm(FlaskForm):
    oxauth_replicas = IntegerField("Number of oxAuth replicas", default=1)
    fido2_replicas = IntegerField("Number of fido2 replicas", default=1)
    scim_replicas = IntegerField("Number of scim replicas", default=1)
    oxtrust_replicas = IntegerField("Number of oxTrust replicas", default=1)
    ldap_replicas = IntegerField("Number of LDAP replicas", default=1)
    oxshibboleth_replicas = IntegerField("Number of oxShibboleth replicas",
                                         default=1)
    oxpassport_replicas = IntegerField("Number of oxPassport replicas",
                                       default=1)
    oxd_server_replicas = IntegerField("Number of oxd-server replicas",
                                       default=1)
    casa_replicas = IntegerField("Number of Casa replicas", default=1)
    radius_replicas = IntegerField("Number of Radius replicas", default=1)


class StorageForm(FlaskForm):
    ldap_storage_size = StringField("Size of ldap volume storage",
                                    default="4Gi")
