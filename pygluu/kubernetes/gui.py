#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
A GUI for installing Gluu Cloud Native Edition.
"""
import ipaddress
import shutil
import json
import os

from pathlib import Path
from flask import Flask, jsonify, make_response, render_template, \
    request, redirect, url_for, send_from_directory

from flask_wtf.csrf import CSRFProtect
from wtforms.validators import InputRequired, Optional, DataRequired
from .common import get_supported_versions, exec_cmd, update_settings_json_file
from .kubeapi import Kubernetes
from .forms import LicenseForm, GluuVersionForm, DeploymentArchForm, \
    GluuNamespaceForm, OptionalServiceForm, GluuGatewayForm, JackrabbitForm, \
    SettingForm, app_volume_types, VolumeTypeForm, ldap_volumes, \
    CacheTypeForm, CouchbaseMultiClusterForm, CouchbaseForm, \
    CouchbaseBackupForm, CouchbaseCalculatorForm, LdapBackupForm, ConfigForm, \
    ImageNameTagForm, ReplicasForm, StorageForm

from .settingdb import SettingDB

app = Flask(__name__, template_folder="templates/gui-install")

cfg = "pygluu.kubernetes.gui_config.DevelopmentConfig"
app_mode = os.environ.get("FLASK_ENV")
if app_mode == "production":
    cfg = "pygluu.kubernetes.gui_config.ProductionConfig"
elif app_mode == "testing":
    cfg = "pygluu.kubernetes.gui_config.TestingConfig"

app.config.from_object(cfg)

csrf = CSRFProtect()
csrf.init_app(app)

wizard_steps = ["license",
                "deployment_arch",
                "set_namespace",
                "optional_settings",
                "install_jackrabbit",
                "settings"]

kubernetes = Kubernetes()

test_arch = ("microk8s", "minikube")
cloud_arch = ("eks", "gke", "aks", "do")
local_arch = "local"

gluu_cache_map = {
    1: "NATIVE_PERSISTENCE",
    2: "IN_MEMORY",
    3: "REDIS",
}

static_files = ["/favicon.ico",
                "/styles.css",
                "/green-logo.svg",
                "/bootstrap.min.css",
                "/bootstrap.min.css.map"]



settings = SettingDB()

@app.before_request
def initialize():
    """
    check accepting license
    """
    if not settings.get("ACCEPT_GLUU_LICENSE") and request.path != "/agreement" and request.path not in static_files:
        return redirect(url_for("agreement"))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(Path("templates/gui-install/static"),
                               'favicon.ico')


@app.route('/styles.css')
def styles():
    return send_from_directory(Path("templates/gui-install/static"), 'styles.css')


@app.route('/green-logo.svg')
def logo():
    return send_from_directory(Path("templates/gui-install/static"), 'green-logo.svg')


@app.route('/bootstrap.min.css')
def bootstrap():
    return send_from_directory(Path("templates/gui-install/static/bootstrap/css"), 'bootstrap.min.css')


@app.route('/bootstrap.min.css.map')
def bootstrap_min_map():
    return send_from_directory(Path("templates/gui-install/static/bootstrap/css"), 'bootstrap.min.css.map')


@app.route("/agreement", methods=["GET", "POST"])
def agreement():
    """Input for Accepting license
    """
    form = LicenseForm()
    if request.method == "POST":
        if form.validate_on_submit():
            next_step = request.form["next_step"]
            settings.set("ACCEPT_GLUU_LICENSE", "Y" if form.accept_gluu_license.data else "N")
            return redirect(url_for(next_step))
        
    with open("./LICENSE", "r") as f:
        agreement_file = f.read()

    if request.method == "GET":
        # populate form
        form.accept_gluu_license.data = settings.get("ACCEPT_GLUU_LICENSE")

    return render_template("index.html",
                           license=agreement_file,
                           form=form,
                           step="agreement",
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
            settings.set("GLUU_VERSION", form.gluu_version.data)
            image_names_and_tags = versions.get(settings.get("GLUU_VERSION"), {})
            settings.update(image_names_and_tags)
            return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form
        form.gluu_version.data = settings.get("GLUU_VERSION")

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
            settings.set("DEPLOYMENT_ARCH", form.deployment_arch.data)
            return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form
        if settings.get("DEPLOYMENT_ARCH"):
            form.deployment_arch.data = settings.get("DEPLOYMENT_ARCH")

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
            settings.set("GLUU_NAMESPACE", form.gluu_namespace.data)
            return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form
        if settings.get("GLUU_NAMESPACE"):
            form.gluu_namespace.data = settings.get("GLUU_NAMESPACE")

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
            data = {}
            next_step = request.form["next_step"]
            data["ENABLE_CACHE_REFRESH"] = form.enable_cache_refresh.data
            data["ENABLE_OXAUTH_KEY_ROTATE"] = form.enable_oxauth_key_rotate.data
            if data["ENABLE_OXAUTH_KEY_ROTATE"] == "Y":
                data["OXAUTH_KEYS_LIFE"] = form.oxauth_key_life.data
            else:
                data["OXAUTH_KEYS_LIFE"] = ""

            data["ENABLE_RADIUS"] = form.enable_radius.data
            if data["ENABLE_RADIUS"] == "Y":
                data["ENABLE_RADIUS_BOOLEAN"] = "true"
            else:
                data["ENABLE_RADIUS_BOOLEAN"] = ""

            data["ENABLE_OXPASSPORT"] = form.enable_oxpassport.data
            if data["ENABLE_OXPASSPORT"] == "Y":
                data["ENABLE_OXPASSPORT_BOOLEAN"] = "true"
            else:
                data["ENABLE_OXPASSPORT_BOOLEAN"] = ""

            data["ENABLE_OXSHIBBOLETH"] = form.enable_shibboleth.data
            if data["ENABLE_OXSHIBBOLETH"] == "Y":
                data["ENABLE_SAML_BOOLEAN"] = "true"
            else:
                data["ENABLE_SAML_BOOLEAN"] = ""

            data["ENABLE_CASA"] = form.enable_casa.data
            if data["ENABLE_CASA"] == "Y":
                data["ENABLE_CASA_BOOLEAN"] = "true"
            else:
                data["ENABLE_CASA_BOOLEAN"] = ""

            data["ENABLE_FIDO2"] = form.enable_fido2.data
            data["ENABLE_SCIM"] = form.enable_scim.data
            data["ENABLE_OXD"] = form.enable_oxd.data

            if data["ENABLE_OXD"] == "Y":
                data["OXD_APPLICATION_KEYSTORE_CN"] = form.oxd_application_keystore_cn.data
                data["OXD_ADMIN_KEYSTORE_CN"] = form.oxd_admin_keystore_cn.data
            else:
                data["OXD_APPLICATION_KEYSTORE_CN"] = ""
                data["OXD_ADMIN_KEYSTORE_CN"] = ""

            data["ENABLE_OXTRUST_API"] = form.enable_oxtrust_api.data
            if data["ENABLE_OXTRUST_API"] == "Y":
                data["ENABLE_OXTRUST_API_BOOLEAN"] = "true"
                data["ENABLE_OXTRUST_TEST_MODE"] = form.enable_oxtrust_test_mode.data
            else:
                data["ENABLE_OXTRUST_API_BOOLEAN"] = ""
                data["ENABLE_OXTRUST_TEST_MODE"] = ""

            if data["ENABLE_OXTRUST_TEST_MODE"] == "Y":
                data["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] = "true"
            else:
                data["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] = ""

            settings.update(data)
            return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

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
            data = {}
            data["INSTALL_GLUU_GATEWAY"] = form.install_gluu_gateway.data

            if data["INSTALL_GLUU_GATEWAY"] == "Y":
                data["ENABLE_OXD"] = "Y"
                data["POSTGRES_NAMESPACE"] = form.postgres_namespace.data
                data["POSTGRES_REPLICAS"] = form.postgres_replicas.data
                data["POSTGRES_URL"] = form.postgres_url.data
                data["KONG_NAMESPACE"] = form.kong_namespace.data
                data["GLUU_GATEWAY_UI_NAMESPACE"] = form.gluu_gateway_ui_namespace.data
                data["KONG_DATABASE"] = form.kong_database.data
                data["KONG_PG_USER"] = form.kong_pg_user.data
                data["KONG_PG_PASSWORD"] = form.kong_pg_password.data
                data["GLUU_GATEWAY_UI_DATABASE"] = form.gluu_gateway_ui_database.data
                data["GLUU_GATEWAY_UI_PG_USER"] = form.gluu_gateway_ui_pg_user.data
                data["GLUU_GATEWAY_UI_PG_PASSWORD"] = form.gluu_gateway_ui_pg_password.data
            else:
                data["ENABLE_OXD"] = "N"
                data["POSTGRES_NAMESPACE"] = ""
                data["POSTGRES_REPLICAS"] = ""
                data["POSTGRES_URL"] = ""
                data["KONG_NAMESPACE"] = ""
                data["GLUU_GATEWAY_UI_NAMESPACE"] = ""
                data["KONG_DATABASE"] = ""
                data["KONG_PG_USER"] = ""
                data["KONG_PG_PASSWORD"] = ""
                data["GLUU_GATEWAY_UI_DATABASE"] = ""
                data["GLUU_GATEWAY_UI_PG_USER"] = ""
                data["GLUU_GATEWAY_UI_PG_PASSWORD"] = ""
            settings.update(data)
            return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)
        form.kong_pg_password_confirm.data = settings.get("KONG_PG_PASSWORD")
        form.gluu_gateway_ui_pg_password_confirm.data = settings.get("GLUU_GATEWAY_UI_PG_PASSWORD")

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
            data = {}
            data["INSTALL_JACKRABBIT"] = form.install_jackrabbit.data
            data["JACKRABBIT_URL"] = form.jackrabbit_url.data
            data["JACKRABBIT_USER"] = form.jackrabbit_user.data

            if data["INSTALL_JACKRABBIT"] == "Y":
                data["JACKRABBIT_URL"] = form.jackrabbit_url.default
                data["JACKRABBIT_USER"] = form.jackrabbit_user.default
                data["JACKRABBIT_STORAGE_SIZE"] = form.jackrabbit_storage_size.data

            settings.update(data)
            return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

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
            next_step = request.form['next_step']
            data = {}
            if not settings.get("TEST_ENVIRONMENT") and settings.get("DEPLOYMENT_ARCH") in test_arch:
                data["TEST_ENVIRONMENT"] = form.test_environment.data

            if settings.get("DEPLOYMENT_ARCH") in cloud_arch or \
                    settings.get("DEPLOYMENT_ARCH") in local_arch:
                data["NODE_SSH_KEY"] = form.node_ssh_key.data

            data["HOST_EXT_IP"] = form.host_ext_ip.data

            if settings.get("DEPLOYMENT_ARCH") == "eks":
                data["AWS_LB_TYPE"] = form.aws_lb_type.data
                data["USE_ARN"] = form.use_arn.data
                data["ARN_AWS_IAM"] = form.arn_aws_iam.data

            if settings.get("DEPLOYMENT_ARCH") == "gke":
                data["GMAIL_ACCOUNT"] = form.gmail_account.data

            if settings.get("APP_VOLUME_TYPE") == 11:
                for node_name in settings.get("NODES_NAMES"):
                    for zone in settings.get("NODES_ZONES"):
                        response, error, retcode = exec_cmd("gcloud compute ssh user@{} --zone={} "
                                                            "--command='echo $HOME'".format(node_name, zone))
                        data["GOOGLE_NODE_HOME_DIR"] = str(response, "utf-8")
                        if data["GOOGLE_NODE_HOME_DIR"]:
                            break
                    if data["GOOGLE_NODE_HOME_DIR"]:
                        break

            data["PERSISTENCE_BACKEND"] = form.persistence_backend.data
            if data["PERSISTENCE_BACKEND"] == "hybrid":
                data["HYBRID_LDAP_HELD_DATA"] = form.hybrid_ldap_held_data.data

            if data["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") or settings.get("INSTALL_JACKRABBIT") == "Y":
                if settings.get("DEPLOYMENT_ARCH") == "microk8s":
                    data["APP_VOLUME_TYPE"] = 1
                elif settings.get("DEPLOYMENT_ARCH") == "minikube":
                    data["APP_VOLUME_TYPE"] = 2

                if data["APP_VOLUME_TYPE"] in (1, 2):
                    next_step = 'cache_type'

            if data["PERSISTENCE_BACKEND"] in ("hybrid", "couchbase"):
                next_step = "couchbase_multi_cluster"

            settings.update(data)

            return redirect(url_for(next_step))

    # TODO: find a way to apply dynamic validation
    if settings.get("DEPLOYMENT_ARCH") == "gke":
        form.gmail_account.validators.append(InputRequired())
    else:
        form.gmail_account.validators.append(Optional())

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("index.html",
                           settings=settings.db,
                           form=form,
                           step="settings",
                           next_step="app_volume_type")


@app.route("/app-volume-type", methods=["GET", "POST"])
def app_volume_type():
    """
    App Volume type Setting
    """
    form = VolumeTypeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            settings["APP_VOLUME_TYPE"] = form.app_volume_type.data

            if settings["APP_VOLUME_TYPE"] in (8, 13):
                settings["LDAP_STATIC_VOLUME_ID"] = form.ldap_static_volume_id.data

            if settings["APP_VOLUME_TYPE"] == 18:
                settings["LDAP_STATIC_DISK_URI"] = form.ldap_static_disk_uri.data

            if settings["DEPLOYMENT_ARCH"] in cloud_arch:
                settings["LDAP_JACKRABBIT_VOLUME"] = form.ldap_jackrabbit_volume.data

            if settings["PERSISTENCE_BACKEND"] in ("hybrid", "couchbase"):
                next_step = "multi-cluster"
            else:
                next_step = request.form['next_step']
            update_settings_json_file(settings)

            return redirect(url_for(next_step))

    if not settings["APP_VOLUME_TYPE"]:
        volume_type = app_volume_types[settings["DEPLOYMENT_ARCH"]]
        form.app_volume_type.label = volume_type["label"]
        form.app_volume_type.choices = volume_type["choices"]
        form.app_volume_type.default = volume_type["default"]

    ldap_volume = ldap_volumes[settings["DEPLOYMENT_ARCH"]]
    form.ldap_jackrabbit_volume.label = ldap_volume["label"]
    form.ldap_jackrabbit_volume.choices = ldap_volume["choices"]

    return render_template("index.html",
                           settings=settings,
                           form=form,
                           step="app_volume_type",
                           next_step="cache_type")


@app.route("/couchbase-multi-cluster", methods=["GET", "POST"])
def couchbase_multi_cluster():
    """
    Deploy multi-cluster settings
    """
    form = CouchbaseMultiClusterForm()

    if request.method == "POST":
        if form.validate_on_submit():
            settings.set("DEPLOY_MULTI_CLUSTER", form.deploy_multi_cluster.data)
            return redirect(url_for(request.form['next_step']))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("index.html",
                           form=form,
                           step="couchbase_multi_cluster",
                           next_step="cache_type")


@app.route("/cache-type", methods=["GET", "POST"])
def cache_type():
    """
    Cache Layer setting
    """
    form = CacheTypeForm()

    if request.method == "POST":
        if form.validate_on_submit():
            data = {}
            data["GLUU_CACHE_TYPE"] = form.gluu_cache_type.data

            if data["GLUU_CACHE_TYPE"] == "REDIS":
                data["REDIS_TYPE"] = form.redis.redis_type.data
                data["INSTALL_REDIS"] = form.redis.install_redis.data

                if data["INSTALL_REDIS"] == "Y":
                    data["REDIS_MASTER_NODES"] = form.redis.redis_master_nodes.data
                    data["REDIS_NODES_PER_MASTER"] = form.redis.redis_nodes_per_master.data
                    data["REDIS_NAMESPACE"] = form.redis.redis_namespace.data
                    data["REDIS_URL"] = "redis-cluster.{}.svc.cluster.local:6379".format(
                        data["REDIS_NAMESPACE"])
                    data["REDIS_PW"] = ""
                else:
                    data["REDIS_MASTER_NODES"] = ""
                    data["REDIS_NODES_PER_MASTER"] = ""
                    data["REDIS_NAMESPACE"] = ""
                    data["REDIS_URL"] = form.redis.redis_url.data
                    data["REDIS_PW"] = form.redis.redis_pw.data

            settings.update(data)

            if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
                return redirect(url_for(request.form['next_step']))

            if settings.get("DEPLOYMENT_ARCH") not in test_arch:
                return redirect(url_for('backup'))

            return redirect(url_for('config'))

    if request.method == "GET":
        form = populate_form_data(form)
        form.redis = populate_form_data(form.redis)
        form.redis.redis_pw_confirm.data = settings.get("REDIS_PW")

    return render_template("index.html",
                           settings=settings,
                           form=form,
                           step="cache_type",
                           next_step="couchbase")


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
            if settings.get("DEPLOYMENT_ARCH") in test_arch:
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
                if settings.get("DEPLOYMENT_ARCH") != "do" or settings.get("DEPLOYMENT_ARCH") != "local":
                    node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                    node_zone_list.append(node_zone)
                node_name_list.append(node_name)

        settings.set("NODES_NAME", node_name_list)
        settings.set("NODES_ZONES", node_zone_list)
        settings.set("NODES_IPS", node_ip_list)

        if settings.get("DEPLOYMENT_ARCH") in ["eks", "gke", "do", "local", "aks"]:
            #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
            ip = "22.22.22.22"
        data = {"status": True, 'ip_address': ip, "message": "Is this the correct external IP address?"}
    except Exception as e:
        app.logger.error(e)
        # prompt for user-inputted IP address
        app.logger.warning("Cannot determine IP address")
        data = {"status": False, 'message': "Cannot determine IP address"}

    return make_response(jsonify(data), 200)


@app.route("/validate_ip/<ip_address>", methods=["GET"])
def validate_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return make_response({"status": True, "message": "IP Address is valid"}, 200)
    except ValueError as exc:
        # raised if IP is invalid
        return make_response({"status": False, "message": "Cannot determine IP address {}".format(exc)}, 400)


def populate_form_data(form):
    # populate form data
    for k, v in form.data.items():
        value = settings.get(k.upper())
        if value:
            form[k].data = value
    return form

