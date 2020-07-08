#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, RadioField, BooleanField, \
    PasswordField, SubmitField, validators, HiddenField, FormField

from wtforms.validators import DataRequired, ValidationError, IPAddress, \
    Email, Optional

from .common import get_supported_versions, prompt_password

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


class LicenseForm(FlaskForm):
    license = RadioField("Do you accept the Gluu license stated above?",
                         choices=[("Y", "Yes"), ("N", "No")], default="N")


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
    gluu_namespace = StringField("Gluu Namespace", default="gluu", validators=[DataRequired()] )


class OptionalServiceForm(FlaskForm):
    enable_cache_refresh = RadioField("Deploy Cr-Rotate", choices=[("Y", "Yes"), ("N", "No")],
                                      default="N", validators=[DataRequired()])
    enable_oxauth_key_rotate = RadioField("Deploy Key-Rotation", choices=[("Y", "Yes"), ("N", "No")],
                                   default="N", validators=[DataRequired()])
    oxauth_key_life = IntegerField("oxAuth keys life in hours", default=48, validators=[DataRequired()])
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
                                              default="oxd-server", validators=[DataRequired()])
    oxd_admin_keystore_cn = StringField("oxd server admin keystore name", default="oxd-server",
                                        validators=[DataRequired()])

    enable_oxtrust_api = RadioField("Enable oxTrust API", choices=[("Y", "Yes"), ("N", "No")],
                                    default="N", validators=[DataRequired()])

    enable_oxtrust_test_mode = RadioField("Enable oxTrust Test Mode", choices=[("Y", "Yes"), ("N", "No")],
                                          default="N", validators=[DataRequired()])

class GluuGatewayForm(FlaskForm):

    install_gluu_gateway = RadioField("Install Gluu Gateway Database mode", choices=[("Y", "Yes"), ("N", "No")],
                                      default="N", validators=[DataRequired()])
    postgres_namespace = StringField("Please enter number of replicas for postgres", default="postgres",
                                     validators=[DataRequired()])
    postgres_replicas = IntegerField("Please enter a namespace for postgres", default=3,
                                     validators=[DataRequired()])
    postgres_url = StringField("Please enter  postgres (remote or local) URL base name. If postgres is to be installed",
                               default="postgres.postgres.svc.cluster.local",
                               validators=[DataRequired()])
    kong_namespace = StringField("Please enter a namespace for Gluu Gateway", default="gluu-gateway",
                                 validators=[DataRequired()])
    gluu_gateway_ui_namespace = StringField("Please enter a namespace for gluu gateway ui", default="gg-ui",
                                            validators=[DataRequired()])
    kong_database = StringField("Please enter gluu-gateway postgres database name", default="kong",
                                validators=[DataRequired()])
    kong_pg_user = StringField("Please enter a user for gluu-gateway postgres database", default="konga",
                               validators=[DataRequired()])
    kong_pg_password = PasswordField("Kong Postgress Password", validators=[DataRequired()])
    kong_pg_password_confirm = PasswordField("Kong Postgress Password Confirmation", validators=[DataRequired()])
    gluu_gateway_ui_database = StringField("Please enter gluu-gateway-ui postgres database name", default="kong",
                                           validators=[DataRequired()])
    gluu_gateway_ui_pg_user = StringField("Please enter a user for gluu-gateway-ui postgres database", default="konga",
                                          validators=[DataRequired()])
    gluu_gateway_ui_pg_password = PasswordField("Gluu Gateway UI postgres password", validators=[DataRequired()])
    gluu_gateway_ui_pg_password_confirm = PasswordField("Gluu Gateway UI postgres password confirmation",
                                                        validators=[DataRequired()])

class JackrabbitForm(FlaskForm):
    install_jackrabbit = RadioField("Install Jackrabbit", choices=[("Y", "Yes"), ("N", "No")],
                                      default="Y", validators=[DataRequired()])
    jackrabbit_url = StringField("Please enter jackrabbit url", default="http://jackrabbit:8080",
                                 validators=[DataRequired()])
    jackrabbit_user = StringField("Please enter jackrabbit user", default="admin", validators=[DataRequired()])
    jackrabbit_storage_size = StringField("Size of Jackrabbit content repository volume storage", default="4Gi")


class SettingForm(FlaskForm):
    test_environment = RadioField("Is this test a test environment?", choices=[("Y", "Yes"), ("N", "No")],
                                      default="N", validators=[DataRequired()])
    node_ssh_key = StringField("Please enter the ssh key path if exists to login into the nodes created[~/.ssh/id_rsa]",
                               default="~/.ssh/id_rsa")
    host_ext_ip = StringField("Please input the host's external IP address", default="127.0.0.1",
                              validators=[DataRequired(), IPAddress()])
    aws_lb_type = RadioField("AWS Loadbalancer type",
                             choices=[("clb", "Classic Load Balancer (CLB)"),
                                      ("nlb", "Network Load Balancer (NLB - Alpha) -- Static IP"),
                                      ("alb", "Application Load Balancer (ALB - Alpha) DEV_ONLY")],
                             default="clb", validators=[DataRequired()])
    use_arn = RadioField("Are you terminating SSL traffic at LB and using certificate from AWS",
                         choices=[("Y", "Yes"), ("N", "No")],
                         default="N")
    arn_aws_iam = StringField("Enter aws-load-balancer-ssl-cert arn quoted ('arn:aws:acm:us-west-2:XXXXXXXX: certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX')",
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
    app_volume_type = RadioField("Local Deployment", choices=[], default="")
    ldap_static_volume_id = StringField("Please enter Persistent Disk Name or EBS Volume ID for LDAP",
                                        description="EBS Volume ID example: vol-049df61146c4d7901")
    ldap_static_disk_uri = StringField("Please enter the disk uri for LDAP",
                                       description="DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                                        "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")

