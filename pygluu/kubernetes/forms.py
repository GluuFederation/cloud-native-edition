#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, RadioField, BooleanField, \
    PasswordField, SubmitField, validators, HiddenField, FormField, FileField, FieldList, \
    MultipleFileField

from wtforms.validators import DataRequired, InputRequired, EqualTo, URL, ValidationError, IPAddress, \
    Email, Optional, Regexp

from .common import get_supported_versions

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

ldap_volumes = {
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


class LicenseForm(FlaskForm):
    license = RadioField("Do you accept the Gluu license stated above?",
                         choices=[("Y", "Yes"), (" ", "No")], default=" ",
                         validators=[DataRequired(message="License has not been accepted")])


class GluuVersionForm(FlaskForm):
    versions, version_number = get_supported_versions()
    supported_versions = []

    for k, v in versions.items():
        if "_dev" in k:
            supported_versions.append((version_number, k))
        else:
            if float(k) > version_number:
                supported_versions.append((version_number, float(k)))

    gluu_version = RadioField("Currently supported versions are :",
                              choices=supported_versions, validators=[DataRequired()])


class DeploymentArchForm(FlaskForm):
    deployment_arch = RadioField("Deployment Arch",
                                 choices=[("microk8s", "Microk8s"),
                                          ("minikube", "MiniKube"),
                                          ("eks", "Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)"),
                                          ("gke", "Google Cloud Engine - Google Kubernetes Engine (GKE)"),
                                          ("aks", "Microsoft Azure (AKS)"),
                                          ("do", "Digital Ocean [BETA]"),
                                          ("local", "Manually provisioned Kubernetes cluster")], default="microk8s",
                                 validators=[DataRequired()])


class GluuNamespaceForm(FlaskForm):
    gluu_namespace = StringField("Gluu Namespace", default="gluu", validators=[InputRequired()])


class OptionalServiceForm(FlaskForm):
    enable_cache_refresh = RadioField("Deploy Cr-Rotate", choices=[("Y", "Yes"), ("N", "No")],
                                      default="N", validators=[DataRequired()])
    enable_oxauth_key_rotate = RadioField("Deploy Key-Rotation", choices=[("Y", "Yes"), ("N", "No")],
                                          default="N", validators=[DataRequired()])
    oxauth_key_life = IntegerField("oxAuth keys life in hours", default=48, validators=[InputRequired()])
    enable_radius = RadioField("Deploy Radius?", choices=[("Y", "Yes"), ("N", "No")],
                               default="N", validators=[DataRequired()])
    enable_oxpassport = RadioField("Deploy Passport", choices=[("Y", "Yes"), ("N", "No")],
                                   default="N", validators=[DataRequired()])
    enable_shibboleth = RadioField("Deploy Shibboleth SAML IDP", choices=[("Y", "Yes"), ("N", "No")],
                                   default="N", validators=[DataRequired()])
    enable_casa = RadioField("Deploy Casa", choices=[("Y", "Yes"), ("N", "No")],
                             default="N", validators=[DataRequired()])
    enable_fido2 = RadioField("Deploy Fido2", choices=[("Y", "Yes"), ("N", "No")],
                              default="N", validators=[DataRequired()])
    enable_scim = RadioField("Deploy scim", choices=[("Y", "Yes"), ("N", "No")],
                             default="N", validators=[DataRequired()])
    enable_oxd = RadioField("Deploy oxd server", choices=[("Y", "Yes"), ("N", "No")],
                            default="N", validators=[DataRequired()])
    # required if oxd enable
    oxd_application_keystore_cn = StringField("oxd server application keystore name",
                                              default="oxd-server", validators=[InputRequired()])
    oxd_admin_keystore_cn = StringField("oxd server admin keystore name", default="oxd-server",
                                        validators=[InputRequired()])

    enable_oxtrust_api = RadioField("Enable oxTrust API", choices=[("Y", "Yes"), ("N", "No")],
                                    default="N", validators=[DataRequired()])

    enable_oxtrust_test_mode = RadioField("Enable oxTrust Test Mode", choices=[("Y", "Yes"), ("N", "No")],
                                          default="N", validators=[DataRequired()])


class GluuGatewayForm(FlaskForm):
    install_gluu_gateway = RadioField("Install Gluu Gateway Database mode", choices=[("Y", "Yes"), ("N", "No")],
                                      default="N", validators=[DataRequired()])
    postgres_namespace = StringField("Please enter number of replicas for postgres", default="postgres",
                                     validators=[InputRequired()])
    postgres_replicas = IntegerField("Please enter a namespace for postgres", default=3,
                                     validators=[InputRequired()])
    postgres_url = StringField("Please enter  postgres (remote or local) URL base name. If postgres is to be installed",
                               default="postgres.postgres.svc.cluster.local",
                               validators=[InputRequired()])
    kong_namespace = StringField("Please enter a namespace for Gluu Gateway", default="gluu-gateway",
                                 validators=[InputRequired()])
    gluu_gateway_ui_namespace = StringField("Please enter a namespace for gluu gateway ui", default="gg-ui",
                                            validators=[InputRequired()])
    kong_database = StringField("Please enter gluu-gateway postgres database name", default="kong",
                                validators=[InputRequired()])
    kong_pg_user = StringField("Please enter a user for gluu-gateway postgres database", default="konga",
                               validators=[InputRequired()])
    kong_pg_password = PasswordField("Kong Postgress Password", validators=[InputRequired(),
                                                                            EqualTo('kong_pg_password_confirm',
                                                                                    message='Passwords do not match')])
    kong_pg_password_confirm = PasswordField("Kong Postgress Password Confirmation", validators=[InputRequired()])
    gluu_gateway_ui_database = StringField("Please enter gluu-gateway-ui postgres database name", default="kong",
                                           validators=[InputRequired()])
    gluu_gateway_ui_pg_user = StringField("Please enter a user for gluu-gateway-ui postgres database", default="konga",
                                          validators=[InputRequired()])
    gluu_gateway_ui_pg_password = PasswordField("Gluu Gateway UI postgres password",
                                                validators=[InputRequired(),
                                                            EqualTo(
                                                                'gluu_gateway_ui_pg_password_confirm',
                                                                message='Passwords do not match')])
    gluu_gateway_ui_pg_password_confirm = PasswordField("Gluu Gateway UI postgres password confirmation",
                                                        validators=[InputRequired()])


class JackrabbitForm(FlaskForm):
    install_jackrabbit = RadioField("Install Jackrabbit", choices=[("Y", "Yes"), ("N", "No")],
                                    default="Y", validators=[DataRequired()])
    jackrabbit_url = StringField("Please enter jackrabbit url", default="http://jackrabbit:8080",
                                 validators=[URL(require_tld=False, message="Url format is wrong")])
    jackrabbit_user = StringField("Please enter jackrabbit user", default="admin", validators=[DataRequired()])
    jackrabbit_storage_size = StringField("Size of Jackrabbit content repository volume storage", default="4Gi")


class SettingForm(FlaskForm):
    test_environment = RadioField("Is this test a test environment?", choices=[("Y", "Yes"), ("N", "No")],
                                  default="N", validators=[DataRequired()])
    node_ssh_key = StringField("Please enter the ssh key path if exists to login into the nodes created[~/.ssh/id_rsa]",
                               default="~/.ssh/id_rsa")
    host_ext_ip = StringField("Please input the host's external IP address", default="127.0.0.1",
                              validators=[InputRequired(), IPAddress()])
    aws_lb_type = RadioField("AWS Loadbalancer type",
                             choices=[("clb", "Classic Load Balancer (CLB)"),
                                      ("nlb", "Network Load Balancer (NLB - Alpha) -- Static IP"),
                                      ("alb", "Application Load Balancer (ALB - Alpha) DEV_ONLY")],
                             default="clb", validators=[DataRequired()])
    use_arn = RadioField("Are you terminating SSL traffic at LB and using certificate from AWS",
                         choices=[("Y", "Yes"), ("N", "No")],
                         default="N")
    arn_aws_iam = StringField(
        "Enter aws-load-balancer-ssl-cert arn quoted "
        "('arn:aws:acm:us-west-2:XXXXXXXX: certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX')",
        render_kw={"disabled": "disabled"})
    gmail_account = StringField("Please enter valid email for Google Cloud account", validators=[Email()])
    persistence_backend = RadioField("Persistence layer",
                                     choices=[("ldap", "WrenDS"),
                                              ("couchbase", "Couchbase [Testing Phase]"),
                                              ("hybrid", "Hybrid(WrenDS + Couchbase)[Testing Phase]")],
                                     default="ldap")
    hybrid_ldap_held_data = RadioField("Hybrid [WrendDS + Couchbase]",
                                       choices=[("default", "Default"), ("user", "User"),
                                                ("site", "Site"), ("cache", "Cache"), ("token", "Token")],
                                       default="default")


class VolumeTypeForm(FlaskForm):
    app_volume_type = RadioField("Local Deployment", choices=[])
    ldap_static_volume_id = StringField("Please enter Persistent Disk Name or EBS Volume ID for LDAP",
                                        description="EBS Volume ID example: vol-049df61146c4d7901",
                                        render_kw={"disabled": "disabled"})
    ldap_static_disk_uri = StringField("Please enter the disk uri for LDAP",
                                       description="DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                                                   "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk",
                                       render_kw={"disabled": "disabled"})
    ldap_jackrabbit_volume = RadioField()


class CouchbaseMultiClusterForm(FlaskForm):
    deploy_multi_cluster = RadioField("Is this a multi-cloud/region setup?", choices=[("Y", "Yes"), ("N", "No")],
                                      description="If you are planning for a multi-cloud/region setup and this is the first cluster answer N"
                                                  "You will answer Y for the second and more cluster setup")


class CacheTypeForm(FlaskForm):
    gluu_cache_type = RadioField("Cache Layer", choices=[(1, 'NATIVE_PERSISTENCE'), (2, 'IN_MEMORY'), (3, 'REDIS')],
                                 default=1)


class RedisForm(FlaskForm):
    redis_type = RadioField("Please select redis Type", choices=[("STANDALONE", "STANDALONE"), ("CLUSTER", "CLUSTER")],
                            default="CLUSTER")
    install_redis = RadioField("Install Redis", choices=[("Y", "Yes"), ("N", "No")], default="Y",
                               description="For the following prompt if placed [N] the Redis is assumed to be"
                                           " installed or remotely provisioned")
    redis_master_nodes = IntegerField("The number of master node. Minimum is 3", default=3,
                                      render_kw={"min": 3})
    redis_nodes_per_master = IntegerField("The number of nodes per master node", default=2)
    redis_namespace = StringField("Please enter a namespace for Redis cluster", default="gluu-redis-cluster")
    redis_pw = PasswordField("Redis Password", render_kw={"disabled": "disabled"})
    redis_pw_confirm = PasswordField("Redis Password Confirmation", render_kw={"disabled": "disabled"})
    redis_url = StringField("Please enter redis URL. If you are deploying redis",
                            default="redis-cluster.gluu-redis-cluster.svc.cluster.local:6379",
                            description="Redis URL can be : redis-cluster.gluu-redis-cluster.svc.cluster.local:6379 in a redis deployment"
                                        "Redis URL using AWS ElastiCach [Configuration Endpoint]: "
                                        "clustercfg.testing-redis.icrbdv.euc1.cache.amazonaws.com:6379",
                            render_kw={"disabled": "disabled"})


class CouchbaseForm(FlaskForm):
    install_couchbase = RadioField("Install Couchbase", choices=[("Y", "Yes"), ("N", "No")],
                                   description="For the following prompt  if placed [N] the couchbase is assumed to be"
                                               " installed or remotely provisioned")
    couchbase_crt = FileField("Couchbase certificate")
    couchbase_cluster_file_override = MultipleFileField("Couchbase override files")
    couchbase_use_low_resources = RadioField("Setup CB nodes using low resources for demo purposes",
                                             choices=[("Y", "Yes"), ("N", "No")])
    couchbase_namespace = StringField("Please enter a namespace for CB objects", default="cbns")
    couchbase_cluster_name = StringField("Please enter a cluster name", default="cbgluu")
    couchbase_url = StringField("Please enter  couchbase (remote or local) URL base name",
                                default="cbgluu.cbns.svc.cluster.local")
    couchbase_user = StringField("Please enter couchbase username", default="admin")
    couchbase_password = PasswordField("Couchbase password")
    couchbase_password_confirmation = PasswordField("Couchbase password confirm")
    couchbase_cn = StringField("Enter Couchbase certificate common name", default="Couchbase CA")


class CouchbaseCalculatorForm(FlaskForm):
    number_of_expected_users = IntegerField("Please enter the number of expected users", default=1000000)
    using_resource_owner_password_cred_grant_flow = RadioField(
        "Will you be using the resource owner password credential grant flow",
        choices=[("Y", "Yes"), ("N", "No")], default="Y")
    using_code_flow = RadioField("Will you be using the code flow", choices=[("Y", "Yes"), ("N", "No")], default="Y")
    using_scim_flow = RadioField("Will you be using the SCIM flow", choices=[("Y", "Yes"), ("N", "No")], default="Y")
    expected_transaction_per_sec = IntegerField("Expected transactions per second", default=2000)
    couchbase_data_nodes = IntegerField("Please enter the number of data nodes. (auto-calculated)", default="")
    couchbase_index_nodes = IntegerField("Please enter the number of index nodes. (auto-calculated)", default="")
    couchbase_query_nodes = IntegerField("Please enter the number of query nodes. (auto-calculated)", default="")
    couchbase_search_eventing_analytics_nodes = IntegerField(
        "Please enter the number of search,eventing and analytics nodes. (auto-calculated)",
        default="")
    chouchbase_general_storage = IntegerField(
        "Please enter the general storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_data_storage = IntegerField("Please enter the data storage size used for couchbase. (auto-calculated)",
                                          default="")
    couchbase_index_storage = IntegerField(
        "Please enter the index node storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_query_storage = IntegerField("Please enter the data storage size used for couchbase. (auto-calculated)",
                                           default="")
    couchbase_analytics_storage = IntegerField(
        "Please enter the analytics node storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_volume_type = RadioField()


class CouchbaseBackupForm(FlaskForm):
    couchbase_incr_backup_schedule = StringField(
        "Please input couchbase backup cron job schedule for incremental backups. "
        "This will run backup job every 30 mins by default.", defalt="*/30 * * * *")
    couchbase_full_backup_schedule = StringField("Please input couchbase backup cron job schedule for full backups. ")
    couchbase_backup_retention_time = StringField("Please enter the time period in which to retain existing backups. "
                                                  "Older backups outside this time frame are deleted", default="168h")
    couchbase_backup_storate_size = StringField("Size of couchbase backup volume storage", default="20Gi")


class LdapBackupForm(FlaskForm):
    ldap_backup_schedule = StringField("Please input ldap backup cron job schedule. "
                                       "This will run backup job every 30 mins by default.", default="*/30 * * * *")


class ConfigForm(FlaskForm):
    gluu_form = StringField("Hostname", default="demoexample.gluu.org")
    country_code = StringField("Country Code", default="US")
    state = StringField("State", default="TX")
    city = StringField("Austin")
    enail = StringField("Email", default="support@gluu.org", validators=[Email()])
    org_name = StringField("Organization", default="Gluu")
    admin_pw = PasswordField("oxTrust Password")
    admin_pw_confirm = PasswordField("oxTrust Password Confirm")
    ldap_pw = PasswordField("LDAP Password")
    ldap_pw_confirm = PasswordField("LDAP Password Confirm")
    is_gluu_fqdn_registered = RadioField("Are you using a globally resolvable FQDN",
                                         choices=[("Y", "Yes"), ("N", "No")],
                                         description="You can mount your FQDN certification and key by placing them inside "
                                                     "gluu.crt and gluu.key respectivley at the same location pygluu-kuberentest.pyz is at.")


class ImageNameTagSet(FlaskForm):
    image_name = StringField()
    image_tag = StringField()


class ImageNameTagForm(FlaskForm):
    edit_image_names_tags = RadioField("Would you like to manually edit the image source/name and tag",
                                       choices=[("Y", "Yes"), ("N", "No")])
    image_name_tags = FieldList(FormField(ImageNameTagSet))


class ReplicasForm(FlaskForm):
    oxauth_replicas = IntegerField("Number of oxAuth replicas", default=1)
    fido_replicas = IntegerField("Number of fido2 replicas", default=1)
    scim_replicas = IntegerField("Number of scim replicas", default=1)
    oxtrust_replicas = IntegerField("Number of oxTrust replicas", default=1)
    ldap_replicas = IntegerField("Number of LDAP replicas", default=1)
    oxshibboleth_replicas = IntegerField("Number of oxShibboleth replicas", default=1)
    oxpassport_replicas = IntegerField("Number of oxPassport replicas", default=1)
    oxd_server_replicas = IntegerField("Number of oxd-server replicas", default=1)
    casa_replicas = IntegerField("Number of Casa replicas", default=1)
    radius_replicas = IntegerField("Number of Radius replicas", default=1)


class StorageForm(FlaskForm):
    ldap_storage_size = StringField("Size of ldap volume storage", default="4Gi")
