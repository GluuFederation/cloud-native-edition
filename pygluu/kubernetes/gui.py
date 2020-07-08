#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
A GUI for installing Gluu Cloud Native Edition.
"""
from pathlib import Path
from flask import Flask, jsonify, make_response, render_template, render_template, \
    request, redirect, url_for, send_from_directory

from flask_wtf.csrf import CSRFProtect
from wtforms.validators import DataRequired, Optional
from .common import get_supported_versions
from .kubeapi import Kubernetes
from .forms import LicenseForm, GluuVersionForm, DeploymentArchForm, GluuNamespaceForm, \
    OptionalServiceForm, GluuGatewayForm, JackrabbitForm, SettingForm, app_volume_types, \
    VolumeTypeForm

import ipaddress

app = Flask(__name__, template_folder="templates/gui-install")

#TODO move config to a better place
app.config['SECRET_KEY'] = "Your_secret_string"
app.config['DEBUG'] = True

csrf = CSRFProtect(app)
wizard_steps = ["license",
                "deployment_arch",
                "set_namespace",
                "optional_settings",
                "install_jackrabbit",
                "settings"]

kubernetes = Kubernetes()

test_arch = ("microk8s", "minikube")
cloud_arch = ("eks", "gke", "aks", "do")
local_arch = ("local")

default_settings = dict(ACCEPT_GLUU_LICENSE="",
                        GLUU_VERSION="",
                        TEST_ENVIRONMENT="",
                        GLUU_UPGRADE_TARGET_VERSION="",
                        GLUU_HELM_RELEASE_NAME="",
                        NGINX_INGRESS_RELEASE_NAME="",
                        NGINX_INGRESS_NAMESPACE="",
                        INSTALL_GLUU_GATEWAY="",
                        POSTGRES_NAMESPACE="",
                        KONG_NAMESPACE="",
                        GLUU_GATEWAY_UI_NAMESPACE="",
                        KONG_PG_USER="",
                        KONG_PG_PASSWORD="",
                        GLUU_GATEWAY_UI_PG_USER="",
                        GLUU_GATEWAY_UI_PG_PASSWORD="",
                        KONG_DATABASE="",
                        GLUU_GATEWAY_UI_DATABASE="",
                        POSTGRES_REPLICAS="",
                        POSTGRES_URL="",
                        KONG_HELM_RELEASE_NAME="",
                        GLUU_GATEWAY_UI_HELM_RELEASE_NAME="",
                        NODES_IPS=[],
                        NODES_ZONES=[],
                        NODES_NAMES=[],
                        NODE_SSH_KEY="",
                        HOST_EXT_IP="",
                        VERIFY_EXT_IP="",
                        AWS_LB_TYPE="",
                        USE_ARN="",
                        ARN_AWS_IAM="",
                        LB_ADD="",
                        REDIS_URL="",
                        REDIS_TYPE="",
                        REDIS_PW="",
                        REDIS_USE_SSL="false",
                        REDIS_SSL_TRUSTSTORE="",
                        REDIS_SENTINEL_GROUP="",
                        REDIS_MASTER_NODES="",
                        REDIS_NODES_PER_MASTER="",
                        REDIS_NAMESPACE="",
                        INSTALL_REDIS="",
                        INSTALL_JACKRABBIT="",
                        JACKRABBIT_STORAGE_SIZE="",
                        JACKRABBIT_URL="",
                        JACKRABBIT_USER="",
                        DEPLOYMENT_ARCH="",
                        PERSISTENCE_BACKEND="",
                        INSTALL_COUCHBASE="",
                        COUCHBASE_NAMESPACE="",
                        COUCHBASE_VOLUME_TYPE="",
                        COUCHBASE_CLUSTER_NAME="",
                        COUCHBASE_URL="",
                        COUCHBASE_USER="",
                        COUCHBASE_PASSWORD="",
                        COUCHBASE_CRT="",
                        COUCHBASE_CN="",
                        COUCHBASE_SUBJECT_ALT_NAME="",
                        COUCHBASE_CLUSTER_FILE_OVERRIDE="",
                        COUCHBASE_USE_LOW_RESOURCES="",
                        COUCHBASE_DATA_NODES="",
                        COUCHBASE_QUERY_NODES="",
                        COUCHBASE_INDEX_NODES="",
                        COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES="",
                        COUCHBASE_GENERAL_STORAGE="",
                        COUCHBASE_DATA_STORAGE="",
                        COUCHBASE_INDEX_STORAGE="",
                        COUCHBASE_QUERY_STORAGE="",
                        COUCHBASE_ANALYTICS_STORAGE="",
                        COUCHBASE_INCR_BACKUP_SCHEDULE="",
                        COUCHBASE_FULL_BACKUP_SCHEDULE="",
                        COUCHBASE_BACKUP_RETENTION_TIME="",
                        COUCHBASE_BACKUP_STORAGE_SIZE="",
                        LDAP_BACKUP_SCHEDULE="",
                        NUMBER_OF_EXPECTED_USERS="",
                        EXPECTED_TRANSACTIONS_PER_SEC="",
                        USING_CODE_FLOW="",
                        USING_SCIM_FLOW="",
                        USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW="",
                        DEPLOY_MULTI_CLUSTER="",
                        HYBRID_LDAP_HELD_DATA="",
                        LDAP_VOLUME="",
                        APP_VOLUME_TYPE="",
                        LDAP_STATIC_VOLUME_ID="",
                        LDAP_STATIC_DISK_URI="",
                        GLUU_CACHE_TYPE="",
                        GLUU_NAMESPACE="",
                        GLUU_FQDN="",
                        COUNTRY_CODE="",
                        STATE="",
                        EMAIL="",
                        CITY="",
                        ORG_NAME="",
                        GMAIL_ACCOUNT="",
                        GOOGLE_NODE_HOME_DIR="",
                        IS_GLUU_FQDN_REGISTERED="",
                        LDAP_PW="",
                        ADMIN_PW="",
                        OXD_APPLICATION_KEYSTORE_CN="",
                        OXD_ADMIN_KEYSTORE_CN="",
                        LDAP_STORAGE_SIZE="",
                        OXAUTH_REPLICAS="",
                        OXTRUST_REPLICAS="",
                        LDAP_REPLICAS="",
                        OXSHIBBOLETH_REPLICAS="",
                        OXPASSPORT_REPLICAS="",
                        OXD_SERVER_REPLICAS="",
                        CASA_REPLICAS="",
                        RADIUS_REPLICAS="",
                        FIDO2_REPLICAS="",
                        SCIM_REPLICAS="",
                        ENABLE_OXTRUST_API="",
                        ENABLE_OXTRUST_TEST_MODE="",
                        ENABLE_CACHE_REFRESH="",
                        ENABLE_OXD="",
                        ENABLE_FIDO2="",
                        ENABLE_SCIM="",
                        ENABLE_RADIUS="",
                        ENABLE_OXPASSPORT="",
                        ENABLE_OXSHIBBOLETH="",
                        ENABLE_CASA="",
                        ENABLE_OXAUTH_KEY_ROTATE="",
                        ENABLE_OXTRUST_API_BOOLEAN="false",
                        ENABLE_OXTRUST_TEST_MODE_BOOLEAN="false",
                        ENABLE_RADIUS_BOOLEAN="false",
                        ENABLE_OXPASSPORT_BOOLEAN="false",
                        ENABLE_CASA_BOOLEAN="false",
                        ENABLE_SAML_BOOLEAN="false",
                        OXAUTH_KEYS_LIFE="",
                        EDIT_IMAGE_NAMES_TAGS="",
                        CASA_IMAGE_NAME="",
                        CASA_IMAGE_TAG="",
                        CONFIG_IMAGE_NAME="",
                        CONFIG_IMAGE_TAG="",
                        CACHE_REFRESH_ROTATE_IMAGE_NAME="",
                        CACHE_REFRESH_ROTATE_IMAGE_TAG="",
                        CERT_MANAGER_IMAGE_NAME="",
                        CERT_MANAGER_IMAGE_TAG="",
                        LDAP_IMAGE_NAME="",
                        LDAP_IMAGE_TAG="",
                        JACKRABBIT_IMAGE_NAME="",
                        JACKRABBIT_IMAGE_TAG="",
                        OXAUTH_IMAGE_NAME="",
                        OXAUTH_IMAGE_TAG="",
                        FIDO2_IMAGE_NAME="",
                        FIDO2_IMAGE_TAG="",
                        SCIM_IMAGE_NAME="",
                        SCIM_IMAGE_TAG="",
                        OXD_IMAGE_NAME="",
                        OXD_IMAGE_TAG="",
                        OXPASSPORT_IMAGE_NAME="",
                        OXPASSPORT_IMAGE_TAG="",
                        OXSHIBBOLETH_IMAGE_NAME="",
                        OXSHIBBOLETH_IMAGE_TAG="",
                        OXTRUST_IMAGE_NAME="",
                        OXTRUST_IMAGE_TAG="",
                        PERSISTENCE_IMAGE_NAME="",
                        PERSISTENCE_IMAGE_TAG="",
                        RADIUS_IMAGE_NAME="",
                        RADIUS_IMAGE_TAG="",
                        GLUU_GATEWAY_IMAGE_NAME="",
                        GLUU_GATEWAY_IMAGE_TAG="",
                        GLUU_GATEWAY_UI_IMAGE_NAME="",
                        GLUU_GATEWAY_UI_IMAGE_TAG="",
                        UPGRADE_IMAGE_NAME="",
                        UPGRADE_IMAGE_TAG="",
                        CONFIRM_PARAMS="N",
                        )


@app.before_request
def initialize():
    if not default_settings["ACCEPT_GLUU_LICENSE"] and request.path != "/agreement":
        return redirect(url_for("agreement"))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(Path("templates/gui-install/static"), 'favicon.ico')


@app.route("/agreement", methods=["GET", "POST"])
def agreement():
    """Input for Accepting license
    """
    form = LicenseForm()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["ACCEPT_GLUU_LICENSE"] = form.license.data
            return redirect(url_for(next_step))

    with open("./LICENSE", "r") as f:
        agreement_file = f.read()

    return render_template("index.html",
                           license=agreement_file,
                           form=form,
                           step="license",
                           next_step="gluu_version")


@app.route("/gluu_version", methods=["GET", "POST"])
def gluu_version():
    """Input for Gluu versions
    """
    form = GluuVersionForm()
    versions, version_number = get_supported_versions()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["GLUU_VERSION"] = form.gluu_version.data
            image_names_and_tags = versions.get(default_settings["GLUU_VERSION"], {})
            default_settings.update(image_names_and_tags)
            return redirect(url_for(next_step))

    return render_template("index.html",
                           form=form,
                           step="gluu_version",
                           next_step="deployment_arch")


@app.route("/deployment-arch", methods=["GET", "POST"])
def deployment_arch():
    """
    Input for the kubernetes infrastructure used.
    """
    form = DeploymentArchForm()

    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["DEPLOYMENT_ARCH"] = form.deployment_arch.data
            return redirect(url_for(next_step))

    return render_template("index.html",
                           form=form,
                           step="deployment_arch",
                           next_step="gluu_namespace")


@app.route("/gluu-namespace", methods=["GET", "POST"])
def gluu_namespace():
    """
    Input for gluu namespace.
    """
    form = GluuNamespaceForm()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["GLUU_NAMESPACE"] = form.gluu_namespace.data
            return redirect(url_for(next_step))

    return render_template("index.html",
                           step="gluu_namespace",
                           form=form,
                           next_step="optional_services")


@app.route("/optional-services", methods=["GET", "POST"])
def optional_services():
    """
    Input for optional services.
    """
    form = OptionalServiceForm()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["ENABLE_CACHE_REFRESH"] = form.enable_cache_refresh.data
            default_settings["ENABLE_OXAUTH_KEY_ROTATE"] = form.enable_oxauth_key_rotate.data
            if form.enable_oxauth_key_rotate == "Y":
                default_settings["OXAUTH_KEYS_LIFE"] = form.oxauth_key_life.data

            default_settings["ENABLE_RADIUS"] = form.enable_radius.data
            if default_settings["ENABLE_RADIUS"] == "Y":
                default_settings["ENABLE_RADIUS_BOOLEAN"] = "true"

            default_settings["ENABLE_OXPASSPORT"] = form.enable_oxpassport.data
            if default_settings["ENABLE_OXPASSPORT"] == "Y":
                default_settings["ENABLE_OXPASSPORT_BOOLEAN"] = "true"

            default_settings["ENABLE_OXSHIBBOLETH"] = form.enable_shibboleth.data
            if default_settings["ENABLE_OXSHIBBOLETH"] == "Y":
                default_settings["ENABLE_SAML_BOOLEAN"] = "true"

            default_settings["ENABLE_CASA"] = form.enable_casa.data
            if default_settings["ENABLE_CASA"] == "Y":
                default_settings["ENABLE_CASA_BOOLEAN"] = "true"

            default_settings["ENABLE_FIDO2"] = form.enable_fido2.data
            default_settings["ENABLE_SCIM"] = form.enable_scim.data
            default_settings["ENABLE_OXD"] = form.enable_oxd.data

            if default_settings["ENABLE_OXD"] == "Y":
                default_settings["OXD_APPLICATION_KEYSTORE_CN"] = form.oxd_application_keystore_cn.data
                default_settings["OXD_ADMIN_KEYSTORE_CN"] = form.oxd_admin_keystore_cn.data

            default_settings["ENABLE_OXTRUST_API"] = form.enable_oxtrust_api.data
            if default_settings["ENABLE_OXTRUST_API"] == "Y":
                default_settings["ENABLE_OXTRUST_API_BOOLEAN"] = "true"
                default_settings["ENABLE_OXTRUST_TEST_MODE"] = form.enable_oxtrust_test_mode

            if default_settings["ENABLE_OXTRUST_TEST_MODE"] == "Y":
                default_settings["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] = "true"

            return redirect(url_for(next_step))

    return render_template("index.html",
                           form=form,
                           step="optional_services",
                           next_step="gluu_gateway")


@app.route("/gluu-gateway", methods=["GET", "POST"])
def gluu_gateway():
    """
    Input for Gluu Gateway
    """
    form = GluuGatewayForm()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["INSTALL_GLUU_GATEWAY"] = form.install_gluu_gateway.data

            if form.install_gluu_gateway == "Y":
                default_settings["ENABLE_OXD"] = "Y"
                default_settings["POSTGRES_NAMESPACE"] = form.postgres_namespace.data
                default_settings["POSTGRES_REPLICAS"] = form.postgres_replicas.data
                default_settings["POSTGRES_URL"] = form.postgres_url.data
                default_settings["KONG_NAMESPACE"] = form.kong_namespace.data
                default_settings["GLUU_GATEWAY_UI_NAMESPACE"] = form.gluu_gateway_ui_namespace.data
                default_settings["KONG_DATABASE"] = form.kong_database.data
                default_settings["KONG_PG_USER"] = form.kong_pg_user.data
                default_settings["KING_PG_PASSWORD"] = form.kong_pg_password.data
                default_settings["GLUU_GATEWAY_UI_DATABASE"] = form.gluu_gateway_ui_database.data
                default_settings["GLUU_GATEWAY_UI_PG_USER"] = form.gluu_gateway_ui_pg_user.data
                default_settings["GLUU_GATEWAY_UI_PG_PASSWORD"] = form.gluu_gateway_ui_pg_password.data

            return redirect(url_for(next_step))

    return render_template("index.html",
                           step="gluu_gateway",
                           form=form,
                           next_step="install_jackrabbit")


@app.route("/install-jackrabbit", methods=["GET", "POST"])
def install_jackrabbit():
    """
    Install Jackrabbit
    """
    form = JackrabbitForm()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            default_settings["INSTALL_JACKRABBIT"] = form.install_jackrabbit.data
            default_settings["JACKRABBIT_URL"] = form.jackrabbit_url.data
            default_settings["JACKRABBIT_USER"] = form.jackrabbit_user.data

        if form.install_jackrabbit == "Y":
            default_settings["JACKRABBIT_STORAGE_SIZE"] = form.jackrabbit_storage_size.data

        return redirect(url_for(next_step))

    return render_template("index.html",
                           step="install_jackrabbit",
                           form=form,
                           next_step="setting")


@app.route("/settings", methods=["GET", "POST"])
def setting():
    """
    Setup Backend setting
    """
    form = SettingForm()

    if request.method == "POST":
        if form.validate_on_submit():
            if not default_settings["TEST_ENVIRONMENT"] and \
               default_settings["DEPLOYMENT_ARCH"] in test_arch:
                default_settings["TEST_ENVIRONMENT"] = form.test_environment.data

            if default_settings["DEPLOYMENT_ARCH"] in cloud_arch or \
               default_settings["DEPLOYMENT_ARCH"] in local_arch:
                default_settings["NODE_SSH_KEY"] = form.node_ssh_key.data

            default_settings["HOST_EXT_IP"] = form.host_ext_ip.data

            if default_settings["DEPLOYMENT_ARCH"] == "eks":
                default_settings["AWS_LB_TYPE"] = form.aws_lb_type.data
                default_settings["USE_ARN"] = form.use_arn.data
                default_settings["ARN_AWS_IAM"] = form.arn_aws_iam.data

            if default_settings["DEPLOYMENT_ARCH"] == "gke":
                default_settings["GMAIL_ACCOUNT"] = form.gmail_account.data

            if default_settings["APP_VOLUME_TYPE"] == 11:
                for node_name in default_settings["NODES_NAMES"]:
                    for zone in default_settings["NODES_ZONES"]:
                        response, error, retcode = exec_cmd("gcloud compute ssh user@{} --zone={} "
                                                            "--command='echo $HOME'".format(node_name, zone))
                        default_settings["GOOGLE_NODE_HOME_DIR"] = str(response, "utf-8")
                        if default_settings["GOOGLE_NODE_HOME_DIR"]:
                            break
                    if default_settings["GOOGLE_NODE_HOME_DIR"]:
                        break

            default_settings["PERSISTENCE_BACKEND"] = form.persistence_backend.data
            if default_settings["PERSISTENCE_BACKEND"] == "hybrid":
                default_settings["HYBRID_LDAP_HELD_DATA"] = form.hybrid_ldap_held_data.data

            if default_settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") or \
                default_settings["INSTALL_JACKRABBIT"] == "Y":
                if default_settings["DEPLOYMENT_ARCH"] == "microk8s":
                    default_settings["APP_VOLUME_TYPE"] = 1
                elif default_settings["DEPLOYMENT_ARCH"] == "minikube":
                    default_settings["APP_VOLUME_TYPE"] = 2

            next_step = request.form['next_step']
            return redirect(url_for(next_step))

    # TODO: find a way to apply dynamic validation
    if default_settings["DEPLOYMENT_ARCH"] == "gke":
        form.gmail_account.validators.append(DataRequired())
    else:
        form.gmail_account.validators.append(Optional())

    return render_template("index.html",
                           default_settings=default_settings,
                           form=form,
                           step="settings",
                           next_step="app_volume_type")

@app.route("/app-volume-type", methods=["GET", "POST"])
def app_volume_type():
    """
    App Volume type Setting
    """
    form = VolumeTypeForm()
    import pdb; pdb.set_trace()
    if default_settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") or \
       default_settings["INSTALL_JACKRABBIT"] == "Y":

        if not default_settings["APP_VOLUME_TYPE"]:
            volume_type = app_volume_types[default_settings["DEPLOYMENT_ARCH"]]
            form.app_volume_type.label = volume_type["label"]
            form.app_volume_type.choices = volume_type["choices"]
            form.app_volume_type.default = volume_type["default"]

    return render_template("index.html",
                           default_settings=default_settings,
                           form=form,
                           step="app_volume_type",
                           next_step="app_volume_type")

@app.route("/determine_ip", methods=["GET"])
def determine_ip():
    """
    Attempts to detect and return ip automatically. Also set node names, zones, and addresses in a cloud deployment.
    :return:
    """

    ip = ""

    try:
        node_ip_list = []
        node_zone_list = []
        node_name_list = []
        node_list = kubernetes.list_nodes().items

        for node in node_list:
            node_name = node.metadata.name
            node_addresses = kubernetes.read_node(name=node_name).status.addresses
            if default_settings["DEPLOYMENT_ARCH"] in ("microk8s", "minikube"):
                for add in node_addresses:
                    if add.type == "InternalIP":
                        ip = add.address
                        node_ip_list.append(ip)
            else:
                for add in node_addresses:
                    if add.type == "ExternalIP":
                        ip = add.address
                        node_ip_list.append(ip)

                # Digital Ocean does not provide zone support yet
                if self.settings["DEPLOYMENT_ARCH"] != "do" or self.settings["DEPLOYMENT_ARCH"] != "local":
                    node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                    node_zone_list.append(node_zone)
                node_name_list.append(node_name)

        default_settings["NODES_NAME"] = node_name_list
        default_settings["NODES_ZONES"] = node_zone_list
        default_settings["NODES_IPS"] = node_ip_list

        if default_settings["DEPLOYMENT_ARCH"] in ["eks", "gke", "do", "local", "aks"]:
            #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
            ip = "22.22.22.22"
        data = {"status": True, 'ip_address': ip, "message": "Is this the correct external IP address?"}
    except Exception as e:
        app.logger.error(e)
        # prompt for user-inputted IP address
        app.logger.warning("Cannot determine IP address")
        data = { "status": False, 'message': "Cannot determine IP address" }

    return make_response(jsonify(data), 200)

@app.route("/validate_ip/<ip_address>", methods=["GET"])
def validate_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return make_response({ "status": True, "message": "IP Address is valid"}, 200)
    except ValueError as exc:
        # raised if IP is invalid
        return make_response({ "status": False, "message": "Cannot determine IP address {}".format(exc)}, 400)

