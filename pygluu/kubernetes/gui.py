#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
A GUI for installing Gluu Cloud Native Edition.
"""
from flask import Flask, render_template, request, redirect, url_for
from .common import get_supported_versions

app = Flask(__name__, template_folder="templates/gui-install")
wizard_steps = ["license",
                "deployment_arch",
                "set_namespace",
                "optional_settings",
                "install_jackrabbit",
                "settings"]

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


@app.route("/agreement", methods=["GET", "POST"])
def agreement():
    """Input for Accepting license
    """

    if request.method == "POST":
        next_step = request.form["next_step"]
        default_settings["ACCEPT_GLUU_LICENSE"] = request.form["accept_gluu_license"]
        return redirect(url_for(next_step))

    with open("./LICENSE", "r") as f:
        agreement_file = f.read()

    return render_template("index.html",
                           license=agreement_file,
                           step="license",
                           next_step="gluu_version")


@app.route("/gluu_version", methods=["GET", "POST"])
def gluu_version():
    """Input for Gluu versions
    """

    versions, version_number = get_supported_versions()

    if request.method == "POST":
        next_step = request.form["next_step"]
        default_settings["GLUU_VERSION"] = request.form["gluu_version"]
        image_names_and_tags = versions.get(default_settings["GLUU_VERSION"], {})
        default_settings.update(image_names_and_tags)

        return redirect(url_for(next_step))

    supported_versions = []
    for k, v in versions.items():
        if "_dev" in k:
            supported_versions.append((version_number, k))
        else:
            if float(k) > version_number:
                supported_versions.append((version_number, float(k)))

    return render_template("index.html",
                           supported_versions=supported_versions,
                           step="gluu_version",
                           next_step="deployment_arch")


@app.route("/deployment-arch", methods=["GET", "POST"])
def deployment_arch():
    """
    Input for the kubernetes infrastructure used.
    """
    if request.method == "POST":
        next_step = request.form["next_step"]
        default_settings["DEPLOYMENT_ARCH"] = request.form["deployment_arch"]
        return redirect(url_for(next_step))

    return render_template("index.html",
                           step="deployment_arch",
                           next_step="gluu_namespace")


@app.route("/gluu-namespace", methods=["GET", "POST"])
def gluu_namespace():
    """
    Input for gluu namespace.
    """
    if request.method == "POST":
        next_step = request.form["next_step"]
        default_settings["GLUU_NAMESPACE"] = request.form["gluu_namespace"]
        return redirect(url_for(next_step))

    return render_template("index.html",
                           step="gluu_namespace",
                           next_step="optional_services")


@app.route("/optional-services", methods=["GET", "POST"])
def optional_services():
    """
    Input for optional services.
    """
    if request.method == "POST":
        for i in request.form.keys():
            if i == "next_step":
                next_step = request.form[i]
                continue
            default_settings[i.upper()] = request.form[i]

        return redirect(url_for(next_step))

    return render_template("index.html",
                           step="optional_services",
                           next_step="gluu_gateway")

@app.route("/gluu-gateway", methods=["GET", "POST"])
def gluu_gateway():
    """
    Input for Gluu Gateway
    """
    if request.method == "POST":
        if request.form["install_gluu_gateway"] == "N":
            default_settings["INSTALL_GLUU_GATEWAY"] = request.form["install_gluu_gateway"]
            return redirect(url_for(next_step))

        default_settings["ENABLE_OXD"] = "Y"
        for i in request.form.keys():
            if i == "next_step":
                next_step = request.form[i]
                continue
            default_settings[i.upper()] = request.form[i]

        return redirect(url_for(next_step))

    return render_template("index.html",
                           step="gluu_gateway",
                           next_step="install_jackrabbit")

@app.route("/install-jackrabbit", methods=["GET", "POST"])
def install_jackrabbit():
    """
    Install Jackrabbit
    """

    return render_template("index.html",
                           step="install_jackrabbit",
                           next_step="settings")
