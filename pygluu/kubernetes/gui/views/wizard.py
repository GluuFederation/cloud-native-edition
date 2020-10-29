"""
pygluu.kubernetes.gui.views.wizard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contain gui views for user's input settings.json

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import shutil
import json
import base64

from pathlib import Path
from flask import current_app
from flask import Blueprint, render_template, \
    request, redirect, url_for, session
from wtforms.validators import InputRequired, Optional, DataRequired
from werkzeug.utils import secure_filename

from pygluu.kubernetes.helpers import get_supported_versions, \
    exec_cmd, generate_password
from pygluu.kubernetes.helpers import get_logger
from ..extensions import gluu_settings
from ..forms.architecture import DeploymentArchForm
from ..forms.backup import CouchbaseBackupForm, LdapBackupForm
from ..forms.cache import CacheTypeForm
from ..forms.configuration import ConfigurationForm
from ..forms.couchbase import CouchbaseForm, \
    CouchbaseCalculatorForm, CouchbaseMultiClusterForm
from ..forms.environment import EnvironmentForm
from ..forms.gluugateway import GluuGatewayForm
from ..forms.helpers import volume_types, app_volume_types, \
    RequiredIfFieldIn, password_requirement_check
from ..forms.images import ImageNameTagForm
from ..forms.istio import IstioForm
from ..forms.jackrabbit import JackrabbitForm
from ..forms.license import LicenseForm
from ..forms.namespace import NamespaceForm
from ..forms.optionalservices import OptionalServiceForm
from ..forms.persistencebackend import PersistenceBackendForm
from ..forms.replicas import ReplicasForm
from ..forms.version import VersionForm
from ..forms.volumes import VolumeForm
from ..forms.helm import HelmForm
from ..forms.upgrade import UpgradeForm
from ..helpers import determine_ip_nodes, download_couchbase_pkg, \
    is_couchbase_pkg_exist

wizard_blueprint = Blueprint('wizard', __name__, template_folder="templates")
logger = get_logger("gluu-gui")

test_arch = ("microk8s", "minikube")
cloud_arch = ("eks", "gke", "aks", "do")
local_arch = "local"

config_settings = {"hostname": "", "country_code": "", "state": "", "city": "",
                   "admin_pw": "", "ldap_pw": "", "email": "", "org_name": "",
                   "redis_pw": ""}


@wizard_blueprint.before_request
def initialize():
    """
    check accepting license
    """
    if not session.get('finish_endpoint'):
        return redirect(url_for('main.index'))

    if not gluu_settings.db.get("ACCEPT_CN_LICENSE") and \
            request.endpoint not in ("wizard.agreement", "wizard.quit_settings"):
        return redirect(url_for("wizard.agreement"))


@wizard_blueprint.context_processor
def inject_wizard_steps():
    """
    inject wizard_step variable to Jinja
    """
    wizard_steps = [
        {
            "title": "License",
            "url": url_for("wizard.agreement")
        },
        {
            "title": "Gluu version",
            "url": url_for("wizard.gluu_version")
        },
        {
            "title": "Deployment architecture",
            "url": url_for("wizard.deployment_arch")
        },
        {
            "title": "Gluu namespace",
            "url": url_for("wizard.gluu_namespace")
        },
        {
            "title": "Optional Services",
            "url": url_for("wizard.optional_services")
        },
        {
            "title": "Gluu gateway",
            "url": url_for("wizard.gluu_gateway")
        },
        {
            "title": "Install jackrabbit",
            "url": url_for("wizard.install_jackrabbit")
        },
        {
            "title": "Install Istio",
            "url": url_for("wizard.install_istio")
        },
        {
            "title": "Environment Setting",
            "url": url_for("wizard.environment")
        },
        {
            "title": "Persistence backend",
            "url": url_for("wizard.persistence_backend")
        },
        {
            "title": "Volumes",
            "url": url_for("wizard.volumes")
        },
        {
            "title": "Couchbase multi cluster",
            "url": url_for("wizard.couchbase_multi_cluster")
        },
        {
            "title": "Couchbase",
            "url": url_for("wizard.couchbase")
        },
        {
            "title": "Couchbase calculator",
            "url": url_for("wizard.couchbase_calculator")
        },
        {
            "title": "Cache type",
            "url": url_for("wizard.cache_type")
        },
        {
            "title": "Backup",
            "url": url_for("wizard.backup")
        },
        {
            "title": "Configuration",
            "url": url_for("wizard.configuration")
        },
        {
            "title": "Images",
            "url": url_for("wizard.images")
        },
        {
            "title": "Replicas",
            "url": url_for("wizard.replicas")
        }
    ]

    if session["finish_endpoint"] == "main.helm_install":
        wizard_steps.append({
            "title": "Helm Configuration",
            "url": url_for("wizard.helm_config")})

    if session["finish_endpoint"] == "main.upgrade":
        wizard_steps.append({
            "title": "Upgrade Version",
            "url": url_for("wizard.upgrade")})

    return dict(wizard_steps=wizard_steps, total_steps=len(wizard_steps), is_wizard=True)


@wizard_blueprint.route("/license", methods=["GET", "POST"])
def agreement():
    """Input for Accepting license
    """
    form = LicenseForm()
    if form.validate_on_submit():
        gluu_settings.db.set("ACCEPT_CN_LICENSE", "Y" if form.accept_gluu_license.data else "N")
        return redirect(url_for(request.form["next_step"]))

    with open("./LICENSE", "r") as f:
        agreement_file = f.read()

    if request.method == "GET":
        # populate form data from settings
        form.accept_gluu_license.data = gluu_settings.db.get("ACCEPT_CN_LICENSE")

    return render_template("wizard/index.html",
                           license=agreement_file,
                           form=form,
                           current_step=1,
                           template="license",
                           next_step="wizard.gluu_version")


@wizard_blueprint.route("/gluu-version", methods=["GET", "POST"])
def gluu_version():
    """Input for Gluu versions
    """
    versions, version_number = get_supported_versions()
    supported_versions = [(k, k) for k in versions.keys()]

    form = VersionForm()
    form.gluu_version.choices = supported_versions
    form.gluu_version.default = version_number

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        gluu_settings.db.set("CN_VERSION", form.gluu_version.data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form data from settings
        form.gluu_version.data = gluu_settings.db.get("CN_VERSION")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=2,
                           template="gluu_version",
                           prev_step="wizard.agreement",
                           next_step="wizard.deployment_arch")


@wizard_blueprint.route("/deployment-arch", methods=["GET", "POST"])
def deployment_arch():
    """
    Input for the kubernetes infrastructure used.
    """
    form = DeploymentArchForm()

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        gluu_settings.db.set("DEPLOYMENT_ARCH", form.deployment_arch.data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form settings
        form.deployment_arch.data = gluu_settings.db.get("DEPLOYMENT_ARCH")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=3,
                           template="deployment_arch",
                           prev_step="wizard.gluu_version",
                           next_step="wizard.gluu_namespace")


@wizard_blueprint.route("/gluu-namespace", methods=["GET", "POST"])
def gluu_namespace():
    """
    Input for gluu namespace.
    """
    form = NamespaceForm()
    if form.validate_on_submit():
        next_step = request.form["next_step"]
        gluu_settings.db.set("CN_NAMESPACE", form.gluu_namespace.data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form
        if gluu_settings.db.get("CN_NAMESPACE"):
            form.gluu_namespace.data = gluu_settings.db.get("CN_NAMESPACE")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=4,
                           template="gluu_namespace",
                           prev_step="wizard.deployment_arch",
                           next_step="wizard.optional_services")


@wizard_blueprint.route("/optional-services", methods=["GET", "POST"])
def optional_services():
    """
    Input for optional services.
    """
    form = OptionalServiceForm()
    if form.validate_on_submit():
        data = {}
        next_step = request.form["next_step"]
        service_list = {
            'cr-rotate': False,
            'auth-server-key-rotation': False,
            'radius': False,
            'oxpassport': False,
            'oxshibboleth': False,
            'casa': False,
            'fido2': False,
            'scim': False,
            'client-api': False
        }
        data["ENABLE_CACHE_REFRESH"] = form.enable_cache_refresh.data
        if data["ENABLE_CACHE_REFRESH"] == "Y":
            service_list['cr-rotate'] = True

        data["ENABLE_AUTH_SERVER_KEY_ROTATE"] = form.enable_auth_server_key_rotate.data
        if data["ENABLE_AUTH_SERVER_KEY_ROTATE"] == "Y":
            data["AUTH_SERVER_KEYS_LIFE"] = form.auth_server_keys_life.data
            service_list['auth_server-key-rotation'] = True
        else:
            data["AUTH_SERVER_KEYS_LIFE"] = ""

        data["ENABLE_RADIUS"] = form.enable_radius.data
        if data["ENABLE_RADIUS"] == "Y":
            data["ENABLE_RADIUS_BOOLEAN"] = "true"
            service_list['radius'] = True
        else:
            data["ENABLE_RADIUS_BOOLEAN"] = ""

        data["ENABLE_OXPASSPORT"] = form.enable_oxpassport.data
        if data["ENABLE_OXPASSPORT"] == "Y":
            data["ENABLE_OXPASSPORT_BOOLEAN"] = "true"
            service_list['oxpassport'] = True
        else:
            data["ENABLE_OXPASSPORT_BOOLEAN"] = ""

        data["ENABLE_OXSHIBBOLETH"] = form.enable_oxshibboleth.data
        if data["ENABLE_OXSHIBBOLETH"] == "Y":
            data["ENABLE_SAML_BOOLEAN"] = "true"
            service_list['oxshibboleth'] = True
        else:
            data["ENABLE_SAML_BOOLEAN"] = ""

        data["ENABLE_CASA"] = form.enable_casa.data
        if data["ENABLE_CASA"] == "Y":
            data["ENABLE_CASA_BOOLEAN"] = "true"
            service_list['casa'] = True
        else:
            data["ENABLE_CASA_BOOLEAN"] = ""

        data["ENABLE_FIDO2"] = form.enable_fido2.data
        if data["ENABLE_FIDO2"] == "Y":
            service_list['fido2'] = True

        data["ENABLE_SCIM"] = form.enable_scim.data
        if data["ENABLE_SCIM"] == "Y":
            service_list['scim'] = True

        data["ENABLE_CLIENT_API"] = form.enable_client_api.data

        if data["ENABLE_CLIENT_API"] == "Y":
            data["CLIENT_API_APPLICATION_KEYSTORE_CN"] = form.client_api_application_keystore_cn.data
            data["CLIENT_API_ADMIN_KEYSTORE_CN"] = form.client_api_admin_keystore_cn.data
            service_list['client-api'] = True
        else:
            data["CLIENT_API_APPLICATION_KEYSTORE_CN"] = ""
            data["CLIENT_API_ADMIN_KEYSTORE_CN"] = ""

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

        data["ENABLED_SERVICES_LIST"] = gluu_settings.db.get("ENABLED_SERVICES_LIST")
        for service, stat in service_list.items():
            if stat:
                if service not in data["ENABLED_SERVICES_LIST"]:
                    data["ENABLED_SERVICES_LIST"].append(service)
            else:
                if service in data["ENABLED_SERVICES_LIST"]:
                    data["ENABLED_SERVICES_LIST"].remove(service)

        gluu_settings.db.update(data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           form=form,
                           current_step=5,
                           template="optional_services",
                           prev_step="wizard.gluu_namespace",
                           next_step="wizard.gluu_gateway")


@wizard_blueprint.route("/gluu-gateway", methods=["GET", "POST"])
def gluu_gateway():
    """
    Input for Gluu Gateway
    """
    form = GluuGatewayForm()
    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {"INSTALL_GLUU_GATEWAY": form.install_gluu_gateway.data}

        if data["INSTALL_GLUU_GATEWAY"] == "Y":
            data["ENABLED_SERVICES_LIST"] = gluu_settings.db.get("ENABLED_SERVICES_LIST")
            data["ENABLED_SERVICES_LIST"].append("gluu-gateway-ui")
            data["ENABLE_CLIENT_API"] = "Y"
            data["POSTGRES_NAMESPACE"] = form.postgres.postgres_namespace.data
            data["POSTGRES_REPLICAS"] = form.postgres.postgres_replicas.data
            data["POSTGRES_URL"] = form.postgres.postgres_url.data
            data["KONG_NAMESPACE"] = form.kong_namespace.data
            data["GLUU_GATEWAY_UI_NAMESPACE"] = form.gluu_gateway_ui_namespace.data
            data["KONG_DATABASE"] = form.kong_database.data
            data["KONG_PG_USER"] = form.kong_pg_user.data
            data["KONG_PG_PASSWORD"] = form.kong_pg_password.data
            data["GLUU_GATEWAY_UI_DATABASE"] = form.gluu_gateway_ui_database.data
            data["GLUU_GATEWAY_UI_PG_USER"] = form.gluu_gateway_ui_pg_user.data
            data["GLUU_GATEWAY_UI_PG_PASSWORD"] = form.gluu_gateway_ui_pg_password.data
        else:
            data["ENABLE_CLIENT_API"] = "N"
            if not gluu_settings.db.get("POSTGRES_NAMESPACE") and \
                    not gluu_settings.db.get("JACKRABBIT_CLUSTER"):
                data["POSTGRES_NAMESPACE"] = ""
            if not gluu_settings.db.get("POSTGRES_REPLICAS") and \
                    not gluu_settings.db.get("JACKRABBIT_CLUSTER"):
                data["POSTGRES_REPLICAS"] = ""
            if not gluu_settings.db.get("POSTGRES_URL") and \
                    not gluu_settings.db.get("JACKRABBIT_CLUSTER"):
                data["POSTGRES_URL"] = ""
            data["KONG_NAMESPACE"] = ""
            data["GLUU_GATEWAY_UI_NAMESPACE"] = ""
            data["KONG_DATABASE"] = ""
            data["KONG_PG_USER"] = ""
            data["KONG_PG_PASSWORD"] = ""
            data["GLUU_GATEWAY_UI_DATABASE"] = ""
            data["GLUU_GATEWAY_UI_PG_USER"] = ""
            data["GLUU_GATEWAY_UI_PG_PASSWORD"] = ""
        gluu_settings.db.update(data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)
        form.postgres = populate_form_data(form.postgres)
        # populate password suggestion
        if not gluu_settings.db.get("KONG_PG_PASSWORD"):
            form.kong_pg_password_confirm.data = form.kong_pg_password.data = generate_password()
        else:
            form.kong_pg_password_confirm.data = gluu_settings.db.get("KONG_PG_PASSWORD")

        if not gluu_settings.db.get("GLUU_GATEWAY_UI_PG_PASSWORD"):
            form.gluu_gateway_ui_pg_password.data = \
                form.gluu_gateway_ui_pg_password_confirm.data = generate_password()
        else:
            form.gluu_gateway_ui_pg_password_confirm.data = gluu_settings.db.get("GLUU_GATEWAY_UI_PG_PASSWORD")

    next_step = "wizard.install_jackrabbit"
    is_wizard = True
    if session["finish_endpoint"] == "main.install_gg_dbmode":
        next_step = "wizard.setting_summary"
        is_wizard = False
        form.install_gluu_gateway.data = "Y"

    return render_template("wizard/index.html",
                           form=form,
                           current_step=6,
                           template="gluu_gateway",
                           prev_step="wizard.optional_services",
                           next_step=next_step,
                           is_wizard=is_wizard)


@wizard_blueprint.route("/install-jackrabbit", methods=["GET", "POST"])
def install_jackrabbit():
    """
    Install Jackrabbit
    """
    form = JackrabbitForm()
    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {"INSTALL_JACKRABBIT": form.install_jackrabbit.data,
                "JACKRABBIT_URL": form.jackrabbit_url.data,
                "JACKRABBIT_ADMIN_ID": form.jackrabbit_admin_id.data,
                "JACKRABBIT_ADMIN_PASSWORD": form.jackrabbit_admin_password.data,
                "JACKRABBIT_CLUSTER": form.jackrabbit_cluster.data}

        if data["INSTALL_JACKRABBIT"] == "Y":
            data["JACKRABBIT_STORAGE_SIZE"] = form.jackrabbit_storage_size.data

        if data["JACKRABBIT_CLUSTER"] == "Y":
            data["POSTGRES_NAMESPACE"] = form.postgres.postgres_namespace.data
            data["POSTGRES_REPLICAS"] = form.postgres.postgres_replicas.data
            data["POSTGRES_URL"] = form.postgres.postgres_url.data
            data["JACKRABBIT_PG_USER"] = form.jackrabbit_pg_user.data
            data["JACKRABBIT_PG_PASSWORD"] = form.jackrabbit_pg_password.data
            data["JACKRABBIT_DATABASE"] = form.jackrabbit_database.data

        gluu_settings.db.update(data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)
        form.postgres = populate_form_data(form.postgres)
        if not gluu_settings.db.get("JACKRABBIT_ADMIN_PASSWORD"):
            form.jackrabbit_admin_password.data = \
                form.jackrabbit_admin_password_confirmation.data = generate_password(24)
        else:
            form.jackrabbit_admin_password.data = \
                form.jackrabbit_admin_password_confirmation.data = gluu_settings.db.get("JACKRABBIT_ADMIN_PASSWORD")

        if not gluu_settings.db.get("JACKRABBIT_PG_PASSWORD"):
            form.jackrabbit_pg_password.data = \
                form.jackrabbit_pg_password_confirmation.data = generate_password()
        else:
            form.jackrabbit_pg_password.data = \
                form.jackrabbit_pg_password_confirmation.data = gluu_settings.db.get("JACKRABBIT_PG_PASSWORD")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=7,
                           template="install_jackrabbit",
                           prev_step="wizard.gluu_gateway",
                           next_step="wizard.install_istio")


@wizard_blueprint.route("/install-istio", methods=["GET", "POST"])
def install_istio():
    """
    Setup Istio
    Note:
    use_istio_ingress field will be required except for microk8s and minikube
    """
    form = IstioForm()
    if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
        del form.use_istio_ingress
        form.lb_add.validators = [Optional()]
    else:
        form.use_istio_ingress.validators = [DataRequired()]

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {}
        data["USE_ISTIO"] = form.use_istio.data
        if gluu_settings.db.get("DEPLOYMENT_ARCH") not in test_arch:
            data["USE_ISTIO_INGRESS"] = form.use_istio_ingress.data
            data["ENABLED_SERVICES_LIST"] = gluu_settings.db.get("ENABLED_SERVICES_LIST")
            if data["USE_ISTIO_INGRESS"] == "Y":
                data["ENABLED_SERVICES_LIST"].append('cn-istio-ingress')
                data["LB_ADD"] = form.lb_add.data
                data["USE_ISTIO"] = "Y"
            else:
                if 'cn-istio-ingress' in data["ENABLED_SERVICES_LIST"]:
                    data["ENABLED_SERVICES_LIST"].remove('cn-istio-ingress')
                data["LB_ADD"] = ""

        if data["USE_ISTIO"] == "Y":
            data["ISTIO_SYSTEM_NAMESPACE"] = form.istio_system_namespace.data
        else:
            data["ISTIO_SYSTEM_NAMESPACE"] = ""

        gluu_settings.db.update(data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           form=form,
                           current_step=8,
                           template="install_istio",
                           prev_step="wizard.install_jackrabbit",
                           next_step="wizard.environment")


@wizard_blueprint.route("/environment", methods=["GET", "POST"])
def environment():
    """
    Environment Setting
    """
    form = EnvironmentForm()
    # TODO: find a way to apply dynamic validation
    if gluu_settings.db.get("DEPLOYMENT_ARCH") == "gke":
        form.gmail_account.validators.append(InputRequired())
    else:
        form.gmail_account.validators.append(Optional())

    ip_node_data = determine_ip_nodes()

    if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
        form.host_ext_ip.data = ip_node_data['ip']
    else:
        del form.host_ext_ip

    if form.validate_on_submit():
        data = {}
        next_step = request.form['next_step']

        if not gluu_settings.db.get("TEST_ENVIRONMENT") and \
                gluu_settings.db.get("DEPLOYMENT_ARCH") not in test_arch:
            data["TEST_ENVIRONMENT"] = form.test_environment.data

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in cloud_arch or \
                gluu_settings.db.get("DEPLOYMENT_ARCH") in local_arch:
            data["NODE_SSH_KEY"] = form.node_ssh_key.data

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
            data["HOST_EXT_IP"] = form.host_ext_ip.data
        else:
            data["HOST_EXT_IP"] = ip_node_data["ip"]

        data["NODES_NAMES"] = ip_node_data["NODES_NAMES"]
        data["NODES_ZONES"] = ip_node_data["NODES_ZONES"]
        data["NODES_IPS"] = ip_node_data["NODES_IPS"]

        # prompt AWS
        if gluu_settings.db.get("DEPLOYMENT_ARCH") == "eks":
            data["AWS_LB_TYPE"] = form.aws_lb_type.data
            data["USE_ARN"] = form.use_arn.data
            data["ARN_AWS_IAM"] = form.arn_aws_iam.data

        # prompt GKE
        if gluu_settings.db.get("DEPLOYMENT_ARCH") == "gke":
            data["GMAIL_ACCOUNT"] = form.gmail_account.data

            if gluu_settings.db.get("APP_VOLUME_TYPE") == 11:
                for node_name in gluu_settings.db.get("NODES_NAMES"):
                    for zone in gluu_settings.db.get("NODES_ZONES"):
                        response, error, retcode = exec_cmd("gcloud compute ssh user@{} --zone={} "
                                                            "--command='echo $HOME'".format(node_name, zone))
                        data["GOOGLE_NODE_HOME_DIR"] = str(response, "utf-8")
                        if data["GOOGLE_NODE_HOME_DIR"]:
                            break
                    if data["GOOGLE_NODE_HOME_DIR"]:
                        break

        gluu_settings.db.update(data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)
        if form.host_ext_ip:
            form.host_ext_ip.data = ip_node_data['ip']

    return render_template("wizard/index.html",
                           deployment_arch=gluu_settings.db.get("DEPLOYMENT_ARCH"),
                           form=form,
                           current_step=9,
                           template="environment",
                           prev_step="wizard.install_istio",
                           next_step="wizard.persistence_backend")


@wizard_blueprint.route("/persistence-backend", methods=["GET", "POST"])
def persistence_backend():
    """
    Setup Persistence Backend setting
    """
    form = PersistenceBackendForm()
    if form.validate_on_submit():
        next_step = request.form['next_step']
        data = {"PERSISTENCE_BACKEND": form.persistence_backend.data}

        if data["PERSISTENCE_BACKEND"] == "hybrid":
            data["HYBRID_LDAP_HELD_DATA"] = form.hybrid_ldap_held_data.data

        if data["PERSISTENCE_BACKEND"] == "ldap":
            data["ENABLED_SERVICES_LIST"] = gluu_settings.db.get("ENABLED_SERVICES_LIST")
            data["ENABLED_SERVICES_LIST"].append("ldap")

        gluu_settings.db.update(data)

        if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") or \
                gluu_settings.db.get("INSTALL_JACKRABBIT") == "Y":
            if gluu_settings.db.get("DEPLOYMENT_ARCH") == "microk8s":
                gluu_settings.db.set("APP_VOLUME_TYPE", 1)
            elif gluu_settings.db.get("DEPLOYMENT_ARCH") == "minikube":
                gluu_settings.db.set("APP_VOLUME_TYPE", 2)

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch and \
                gluu_settings.db.get("PERSISTENCE_BACKEND") == "couchbase":
            next_step = 'wizard.couchbase'

        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           form=form,
                           current_step=10,
                           template="persistence_backend",
                           prev_step="wizard.environment",
                           next_step="wizard.volumes")


@wizard_blueprint.route("/volumes", methods=["GET", "POST"])
def volumes():
    """
    App Volume type Setting
    """
    form = VolumeForm()

    if gluu_settings.db.get("DEPLOYMENT_ARCH") and \
            gluu_settings.db.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
        volume_type = app_volume_types[gluu_settings.db.get("DEPLOYMENT_ARCH")]
        form.app_volume_type.label = volume_type["label"]
        form.app_volume_type.choices = volume_type["choices"]
        form.app_volume_type.default = volume_type["default"]
        form.app_volume_type.validators = [DataRequired()]
    else:
        del form.app_volume_type

    if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
        ldap_volume = volume_types[gluu_settings.db.get("DEPLOYMENT_ARCH")]
        form.ldap_jackrabbit_volume.label = ldap_volume["label"]
        form.ldap_jackrabbit_volume.choices = ldap_volume["choices"]
        form.ldap_jackrabbit_volume.validators = [RequiredIfFieldIn('app_volume_type', [7, 12, 17])]
    else:
        del form.ldap_jackrabbit_volume

    # TODO: find a way to apply dynamic validation
    if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
        if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
            form.ldap_static_volume_id.validators = [RequiredIfFieldIn("app_volume_type", [8, 13])]
            form.ldap_static_disk_uri.validators = [RequiredIfFieldIn("app_volume_type", [18])]
        form.ldap_storage_size.validators = [InputRequired()]
    else:
        form.ldap_storage_size.validators = [Optional()]
        if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
            del form.ldap_static_volume_id
            del form.ldap_static_disk_uri

    if form.validate_on_submit():
        data = {"APP_VOLUME_TYPE": gluu_settings.db.get("APP_VOLUME_TYPE")}
        if form.app_volume_type:
            data["APP_VOLUME_TYPE"] = form.app_volume_type.data

        if data["APP_VOLUME_TYPE"] in (8, 13):
            data["LDAP_STATIC_VOLUME_ID"] = form.ldap_static_volume_id.data
        else:
            data["LDAP_STATIC_VOLUME_ID"] = ""

        if data["APP_VOLUME_TYPE"] == 18:
            data["LDAP_STATIC_DISK_URI"] = form.ldap_static_disk_uri.data
        else:
            data["LDAP_STATIC_DISK_URI"] = ""

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke") and \
                form.ldap_jackrabbit_volume.data and data["APP_VOLUME_TYPE"] in [7, 12, 17]:
            data["LDAP_JACKRABBIT_VOLUME"] = form.ldap_jackrabbit_volume.data
        else:
            data["LDAP_JACKRABBIT_VOLUME"] = ""

        if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
            data["LDAP_STORAGE_SIZE"] = form.ldap_storage_size.data

        gluu_settings.db.update(data)

        if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            next_step = request.form['next_step']
        else:
            next_step = 'wizard.cache_type'

        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           deployment_arch=gluu_settings.db.get('DEPLOYMENT_ARCH'),
                           persistence_backend=gluu_settings.db.get("PERSISTENCE_BACKEND"),
                           form=form,
                           current_step=11,
                           template="app_volume_type",
                           prev_step="wizard.persistence_backend",
                           next_step="wizard.couchbase_multi_cluster")


@wizard_blueprint.route("/couchbase-multi-cluster", methods=["GET", "POST"])
def couchbase_multi_cluster():
    """
    Deploy multi-cluster settings
    """
    form = CouchbaseMultiClusterForm()
    if form.validate_on_submit():
        gluu_settings.db.set("DEPLOY_MULTI_CLUSTER", form.deploy_multi_cluster.data)
        return redirect(url_for(request.form['next_step']))

    if request.method == "GET":
        form = populate_form_data(form)

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.persistence_backend"
    if gluu_settings.db.get("APP_VOLUME_TYPE") not in (1, 2):
        prev_step = "wizard.volumes"

    return render_template("wizard/index.html",
                           form=form,
                           current_step=12,
                           template="couchbase_multi_cluster",
                           prev_step=prev_step,
                           next_step="wizard.couchbase")


@wizard_blueprint.route("/couchbase", methods=["GET", "POST"])
def couchbase():
    form = CouchbaseForm()

    if is_couchbase_pkg_exist():
        del form.package_url

    custom_cb_ca_crt = Path("./couchbase_crts_keys/ca.crt")
    custom_cb_crt = Path("./couchbase_crts_keys/chain.pem")
    custom_cb_key = Path("./couchbase_crts_keys/pkey.key")

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {"INSTALL_COUCHBASE": form.install_couchbase.data}
        if data["INSTALL_COUCHBASE"] == "N":
            filename = secure_filename(form.couchbase_crt.data.filename)
            form.couchbase_crt.data.save('./' + filename)
            with open(Path('./' + filename)) as content_file:
                ca_crt = content_file.read()
                encoded_ca_crt_bytes = base64.b64encode(ca_crt.encode("utf-8"))
                encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
                data["COUCHBASE_CRT"] = encoded_ca_crt_string
        else:
            data["COUCHBASE_CRT"] = ""

        data["COUCHBASE_CLUSTER_FILE_OVERRIDE"] = form.couchbase_cluster_file_override.data
        if data["COUCHBASE_CLUSTER_FILE_OVERRIDE"] == "Y":

            for file in form.couchbase_cluster_files.data:
                filename = secure_filename(file.filename)
                file.save('./' + filename)

            try:
                shutil.copy(Path("./couchbase-cluster.yaml"),
                            Path("./couchbase/couchbase-cluster.yaml"))
                shutil.copy(Path("./couchbase-buckets.yaml"),
                            Path("./couchbase/couchbase-buckets.yaml"))
                shutil.copy(Path("./couchbase-ephemeral-buckets.yaml"),
                            Path("./couchbase/couchbase-ephemeral-buckets.yaml"))
            except FileNotFoundError:
                current_app.logger.error("An override option has been chosen but "
                                         "there is a missing couchbase file that "
                                         "could not be found at the current path.")

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
            data["COUCHBASE_USE_LOW_RESOURCES"] = "Y"
        else:
            data["COUCHBASE_USE_LOW_RESOURCES"] = form.couchbase_use_low_resources.data

        data["COUCHBASE_NAMESPACE"] = form.couchbase_namespace.data
        data["COUCHBASE_CLUSTER_NAME"] = form.couchbase_cluster_name.data
        data["COUCHBASE_URL"] = form.couchbase_url.data
        data["COUCHBASE_SUPERUSER"] = form.couchbase_superuser.data
        data["COUCHBASE_SUPERUSER_PASSWORD"] = form.couchbase_superuser_password.data
        data["COUCHBASE_USER"] = form.couchbase_user.data
        data["COUCHBASE_PASSWORD"] = form.couchbase_password.data

        if not custom_cb_ca_crt.exists() or \
                not custom_cb_crt.exists() and not custom_cb_key.exists():
            data['COUCHBASE_SUBJECT_ALT_NAME'] = [
                "*.{}".format(data["COUCHBASE_CLUSTER_NAME"]),
                "*.{}.{}".format(data["COUCHBASE_CLUSTER_NAME"],
                                 data["COUCHBASE_NAMESPACE"]),
                "*.{}.{}.svc".format(data["COUCHBASE_CLUSTER_NAME"],
                                     data["COUCHBASE_NAMESPACE"]),
                "{}-srv".format(data["COUCHBASE_CLUSTER_NAME"]),
                "{}-srv.{}".format(data["COUCHBASE_CLUSTER_NAME"],
                                   data["COUCHBASE_NAMESPACE"]),
                "{}-srv.{}.svc".format(data["COUCHBASE_CLUSTER_NAME"],
                                       data["COUCHBASE_NAMESPACE"]),
                "localhost"
            ]
            data["COUCHBASE_CN"] = form.couchbase_cn.data

        gluu_settings.db.update(data)

        if gluu_settings.db.get("COUCHBASE_USE_LOW_RESOURCES") == "N" and \
                gluu_settings.db.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "N" and \
                gluu_settings.db.get("INSTALL_COUCHBASE") == "Y":
            return redirect(url_for("wizard.couchbase_calculator"))

        # download couchbase
        if gluu_settings.db.get("INSTALL_COUCHBASE") == "Y" and not is_couchbase_pkg_exist():
            download_couchbase_pkg(form.package_url.data)

        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

        if not gluu_settings.db.get("COUCHBASE_PASSWORD"):
            form.couchbase_password.data = \
                form.couchbase_password_confirmation.data = generate_password()
        else:
            form.couchbase_password_confirmation.data = gluu_settings.db.get("COUCHBASE_PASSWORD")

        if not gluu_settings.db.get("COUCHBASE_SUPERUSER_PASSWORD"):
            form.couchbase_superuser_password.data = \
                form.couchbase_superuser_password_confirmation.data = generate_password()
        else:
            form.couchbase_superuser_password_confirmation.data = gluu_settings.db.get("COUCHBASE_SUPERUSER_PASSWORD")

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
            form.couchbase_use_low_resources.validators = [Optional()]
            form.couchbase_use_low_resources.data = "Y"
        else:
            form.couchbase_use_low_resources.validators = [DataRequired()]

        if not custom_cb_ca_crt.exists() or \
                not custom_cb_crt.exists() and not custom_cb_key.exists():
            form.couchbase_cn.validators = [InputRequired()]
        else:
            form.couchbase_cn.validators = [Optional()]
            form.couchbase_cn.render_kw = {"disabled": "disabled"}

    return render_template("wizard/index.html",
                           form=form,
                           current_step=13,
                           template="couchbase",
                           prev_step="wizard.couchbase_multi_cluster",
                           next_step="wizard.cache_type")


@wizard_blueprint.route("/couchbase-calculator", methods=["GET", "POST"])
def couchbase_calculator():
    """
    Attempt to Calculate resources needed
    """

    form = CouchbaseCalculatorForm()

    # override couchbase_volume_type with
    # dynamic value of volume_type based on deployment arch value
    if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke") and \
            not gluu_settings.db.get("COUCHBASE_VOLUME_TYPE"):
        volume_type = volume_types[gluu_settings.db.get("DEPLOYMENT_ARCH")]
        form.couchbase_volume_type.choices = volume_type["choices"]
        form.couchbase_volume_type.validators = [DataRequired()]

    if form.validate_on_submit():
        data = {}
        for field in form:
            if field.name == "csrf_token":
                continue
            data[field.name.upper()] = field.data

        gluu_settings.db.update(data)
        return redirect(url_for(request.form["next_step"]))

    return render_template("wizard/index.html",
                           form=form,
                           current_step=14,
                           template="couchbase_calculator",
                           prev_step="wizard.couchbase",
                           next_step="wizard.cache_type")


@wizard_blueprint.route("/cache-type", methods=["GET", "POST"])
def cache_type():
    """
    Cache Layer setting
    """
    form = CacheTypeForm()
    if form.validate_on_submit():
        data = {"CN_CACHE_TYPE": form.gluu_cache_type.data}

        if data["CN_CACHE_TYPE"] == "REDIS":
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

        gluu_settings.db.update(data)

        # skip backup form if deployment_arch is microk8s or minikube
        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
            return redirect(url_for('wizard.configuration'))

        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)
        form.redis = populate_form_data(form.redis)
        form.redis.redis_pw_confirm.data = gluu_settings.db.get("REDIS_PW")

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.volumes"
    if gluu_settings.db.get("DEPLOY_MULTI_CLUSTER"):
        prev_step = "wizard.couchbase_multi_cluster"
    elif gluu_settings.db.get("INSTALL_COUCHBASE") == "Y":
        prev_step = "wizard.couchbase"

    return render_template("wizard/index.html",
                           form=form,
                           current_step=15,
                           template="cache_type",
                           prev_step=prev_step,
                           next_step="wizard.backup")


@wizard_blueprint.route("/backup", methods=["GET", "POST"])
def backup():
    if not gluu_settings.db.get("PERSISTENCE_BACKEND"):
        return redirect(url_for('wizard.setting'))

    form = CouchbaseBackupForm()

    if gluu_settings.db.get("PERSISTENCE_BACKEND") == "ldap":
        form = LdapBackupForm()

    if form.validate_on_submit():
        data = {}
        if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            data["COUCHBASE_INCR_BACKUP_SCHEDULE"] = form.couchbase_incr_backup_schedule.data
            data["COUCHBASE_FULL_BACKUP_SCHEDULE"] = form.couchbase_full_backup_schedule.data
            data["COUCHBASE_BACKUP_RETENTION_TIME"] = form.couchbase_backup_retention_time.data
            data["COUCHBASE_BACKUP_STORAGE_SIZE"] = form.couchbase_backup_storage_size.data
        elif gluu_settings.db.get("PERSISTENCE_BACKEND") == "ldap":
            data["LDAP_BACKUP_SCHEDULE"] = form.ldap_backup_schedule.data

        gluu_settings.db.update(data)
        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           persistence_backend=gluu_settings.db.get("PERSISTENCE_BACKEND"),
                           form=form,
                           current_step=16,
                           template="backup",
                           prev_step="wizard.cache_type",
                           next_step="wizard.configuration")


@wizard_blueprint.route("/configuration", methods=["GET", "POST"])
def configuration():
    form = ConfigurationForm()

    # override ldap_pw validators
    if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
        form.ldap_pw.validators = [InputRequired(), password_requirement_check()]
    else:
        form.ldap_pw.validators = [Optional()]
        form.ldap_pw.render_kw = {"disabled": "disabled"}

    if form.validate_on_submit():
        data = {"CN_FQDN": form.gluu_fqdn.data,
                "COUNTRY_CODE": form.country_code.data,
                "STATE": form.state.data,
                "CITY": form.city.data,
                "EMAIL": form.email.data,
                "ORG_NAME": form.org_name.data,
                "ADMIN_PW": form.admin_pw.data}

        if gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
            data["LDAP_PW"] = form.ldap_pw.data
        else:
            data["LDAP_PW"] = gluu_settings.db.get("COUCHBASE_PASSWORD")

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
            data["IS_CN_FQDN_REGISTERED"] = "N"
        else:
            data["IS_CN_FQDN_REGISTERED"] = form.is_gluu_fqdn_registered.data

        if data["IS_CN_FQDN_REGISTERED"] == "N":
            data["ENABLED_SERVICES_LIST"] = gluu_settings.db.get("ENABLED_SERVICES_LIST")
            data["ENABLED_SERVICES_LIST"].append("update-lb-ip")
        gluu_settings.db.update(data)
        generate_main_config()

        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)
        if not gluu_settings.db.get("ADMIN_PW"):
            form.admin_pw.data = form.admin_pw_confirm.data = generate_password()
        else:
            form.admin_pw_confirm.data = gluu_settings.db.get("ADMIN_PW")

        if not gluu_settings.db.get("LDAP_PW"):
            form.ldap_pw.data = form.ldap_pw_confirm.data = generate_password()
        else:
            form.ldap_pw_confirm.data = gluu_settings.db.get("LDAP_PW")

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in test_arch:
            form.is_gluu_fqdn_registered.validators = [Optional()]
            form.is_gluu_fqdn_registered.data = "N"
        else:
            form.is_gluu_fqdn_registered.validators = [DataRequired()]

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.backup"
    if gluu_settings.db.get("APP_VOLUME_TYPE") in (1, 2):
        prev_step = "wizard.cache_type"

    return render_template("wizard/index.html",
                           deployment_arch=gluu_settings.db.get("DEPLOYMENT_ARCH"),
                           persistence_backend=gluu_settings.db.get("PERSISTENCE_BACKEND"),
                           form=form,
                           current_step=17,
                           template="config",
                           prev_step=prev_step,
                           next_step="wizard.images")


@wizard_blueprint.route("/images", methods=["POST", "GET"])
def images():
    form = ImageNameTagForm()
    collapsed_ids = []

    # hide the fields if the services is not enabled; note that we still
    # need the data left intact
    if gluu_settings.db.get("ENABLE_CASA") == "N":
        collapsed_ids += [
            form.casa_image_name.id,
            form.casa_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_CACHE_REFRESH") == "N":
        collapsed_ids += [
            form.cache_refresh_rotate_image_name.id,
            form.cache_refresh_rotate_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_AUTH_SERVER_KEY_ROTATE") == "N":
        collapsed_ids += [
            form.cert_manager_image_name.id,
            form.cert_manager_image_tag.id,
        ]

    if gluu_settings.db.get("PERSISTENCE_BACKEND") not in ("hybrid", "ldap"):
        collapsed_ids += [
            form.ldap_image_name.id,
            form.ldap_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_CLIENT_API") == "N":
        collapsed_ids += [
            form.client_api_image_name.id,
            form.client_api_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_OXPASSPORT") == "N":
        collapsed_ids += [
            form.oxpassport_image_name.id,
            form.oxpassport_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_OXSHIBBOLETH") == "N":
        collapsed_ids += [
            form.oxshibboleth_image_name.id,
            form.oxshibboleth_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_RADIUS") == "N":
        collapsed_ids += [
            form.radius_image_name.id,
            form.radius_image_tag.id,
        ]

    if gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "N":
        collapsed_ids += [
            form.gluu_gateway_image_name.id,
            form.gluu_gateway_image_tag.id,
            form.gluu_gateway_ui_image_name.id,
            form.gluu_gateway_ui_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_FIDO2") == "N":
        collapsed_ids += [
            form.fido2_image_name.id,
            form.fido2_image_tag.id,
        ]

    if gluu_settings.db.get("ENABLE_SCIM") == "N":
        collapsed_ids += [
            form.scim_image_name.id,
            form.scim_image_tag.id,
        ]

    if form.validate_on_submit():
        data = {}
        for field in form:
            if field.name == "csrf_token":
                continue
            data[field.name.upper()] = field.data
        data["EDIT_IMAGE_NAMES_TAGS"] = "N"
        gluu_settings.db.update(data)
        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        # get default images
        versions, _ = get_supported_versions()
        image_names_tags = versions.get(gluu_settings.db.get("CN_VERSION"), {})

        for k, v in image_names_tags.items():
            field = getattr(form, k.lower(), None)
            if not field:
                continue
            field.data = v
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           form=form,
                           current_step=18,
                           template="image_name_tag",
                           prev_step="wizard.configuration",
                           next_step="wizard.replicas",
                           collapsed_ids=collapsed_ids)


@wizard_blueprint.route("/replicas", methods=["POST", "GET"])
def replicas():
    form = ReplicasForm()

    # modify form, remove the form if the services is not enabled
    if gluu_settings.db.get("ENABLE_FIDO2") == "N":
        del form.fido2_replicas
    if gluu_settings.db.get("ENABLE_SCIM") == "N":
        del form.scim_replicas
    if gluu_settings.db.get("PERSISTENCE_BACKEND") not in ("hybrid", "ldap"):
        del form.ldap_replicas
    if gluu_settings.db.get("ENABLE_OXSHIBBOLETH") == "N":
        del form.oxshibboleth_replicas
    if gluu_settings.db.get("ENABLE_OXPASSPORT") == "N":
        del form.oxpassport_replicas
    if gluu_settings.db.get("ENABLE_CLIENT_API") == "N":
        del form.client_api_server_replicas
    if gluu_settings.db.get("ENABLE_CASA") == "N":
        del form.casa_replicas
    if gluu_settings.db.get("ENABLE_RADIUS") == "N":
        del form.radius_replicas

    if form.validate_on_submit():
        data = {}
        for field in form:
            if field.name == "csrf_token":
                continue
            data[field.name.upper()] = field.data

        gluu_settings.db.update(data)
        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)

    next_step = "wizard.setting_summary"
    if session["finish_endpoint"] == "main.helm_install":
        next_step = "wizard.helm_config"
    elif session["finish_endpoint"] == "main.upgrade":
        next_step = "wizard.upgrade"

    return render_template("wizard/index.html",
                           form=form,
                           current_step=19,
                           template="replicas",
                           prev_step="wizard.images",
                           next_step=next_step)


@wizard_blueprint.route("/helm-configuration", methods=["POST", "GET"])
def helm_config():
    form = HelmForm()
    if form.validate_on_submit():
        data = {"CN_HELM_RELEASE_NAME": form.gluu_helm_release_name.data,
                "NGINX_INGRESS_RELEASE_NAME": form.nginx_ingress_release_name.data,
                "NGINX_INGRESS_NAMESPACE": form.nginx_ingress_namespace.data}

        if gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "Y":
            data["KONG_HELM_RELEASE_NAME"] = form.kong_helm_release_name.data
            data["GLUU_GATEWAY_UI_HELM_RELEASE_NAME"] = form.gluu_gateway_ui_helm_release_name.data

        gluu_settings.db.update(data)
        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)
    install_gluu_gateway = gluu_settings.db.get("INSTALL_GLUU_GATEWAY")
    return render_template("wizard/index.html",
                           form=form,
                           current_step=20,
                           template="helm",
                           install_gluu_gateway=install_gluu_gateway,
                           prev_step="wizard.replicas",
                           next_step="wizard.setting_summary")


@wizard_blueprint.route("/gluu-upgrade", methods=["POST", "GET"])
def upgrade():
    form = UpgradeForm()
    if form.validate_on_submit():
        data = {"ENABLED_SERVICES_LIST": gluu_settings.db.get("ENABLED_SERVICES_LIST")}
        data["ENABLED_SERVICES_LIST"].append("upgrade")
        data["CN_UPGRADE_TARGET_VERSION"] = form.upgrade_target_version.data
        gluu_settings.db.update(data)
        # get supported versions image name and tag
        versions, version_number = get_supported_versions()
        image_names_and_tags = versions.get(gluu_settings.db.get("CN_UPGRADE_TARGET_VERSION"), {})
        custom_images = []
        for k, v in image_names_and_tags.items():
            if "IMAGE_NAME" in k and gluu_settings.db.get(k) != v:
                image = '_'.join(k.split("_")[:2])
                custom_images.append(f"{image}_NAME")
                custom_images.append(f"{image}_TAG")

        for k, v in image_names_and_tags.items():
            if k not in custom_images:
                gluu_settings.db.set(k, v)

        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           form=form,
                           current_step=20,
                           template="upgrade",
                           prev_step="wizard.replicas",
                           next_step="wizard.setting_summary")


@wizard_blueprint.route("/setting-summary", methods=["POST", "GET"])
def setting_summary():
    """
    Formats output of settings from prompts to the user.
    Passwords are not displayed.
    """
    hidden_settings = ["NODES_IPS", "NODES_ZONES", "NODES_NAMES",
                       "COUCHBASE_PASSWORD", "LDAP_PW", "ADMIN_PW", "REDIS_PW",
                       "COUCHBASE_SUBJECT_ALT_NAME", "KONG_PG_PASSWORD",
                       "GLUU_GATEWAY_UI_PG_PASSWORD", "JACKRABBIT_ADMIN_PASSWORD",
                       "JACKRABBIT_PG_PASSWORD"]

    return render_template("wizard/setting_summary.html",
                           hidden_settings=hidden_settings,
                           settings=gluu_settings.db.get_all())


@wizard_blueprint.route("/quit", methods=["POST"])
def quit_settings():
    """
    Quit installation wizard and discard settings.json
    """
    if request.form["quit_confirm"] == "yes":
        gluu_settings.db.reset_data()
    return redirect(url_for('main.index'))


@wizard_blueprint.route("/new")
def new():
    """
    New installation wizard and discard current settings.json
    """
    gluu_settings.db.reset_data()
    return redirect(url_for('wizard.agreement'))


def populate_form_data(form):
    """
    populate form data from settings
    """
    for k, _ in form.data.items():
        if k == "csrf_token":
            continue

        value = gluu_settings.db.get(k.upper())
        if value:
            form[k].data = value
    return form


def generate_main_config():
    """
    Prepare generate.json and output it
    """
    config_settings["hostname"] = gluu_settings.db.get("CN_FQDN")
    config_settings["country_code"] = gluu_settings.db.get("COUNTRY_CODE")
    config_settings["state"] = gluu_settings.db.get("STATE")
    config_settings["city"] = gluu_settings.db.get("CITY")
    config_settings["admin_pw"] = gluu_settings.db.get("ADMIN_PW")
    config_settings["ldap_pw"] = gluu_settings.db.get("LDAP_PW")
    config_settings["redis_pw"] = gluu_settings.db.get("REDIS_PW")
    if gluu_settings.db.get("PERSISTENCE_BACKEND") == "couchbase":
        config_settings["ldap_pw"] = gluu_settings.db.get("COUCHBASE_PASSWORD")
    config_settings["email"] = gluu_settings.db.get("EMAIL")
    config_settings["org_name"] = gluu_settings.db.get("ORG_NAME")

    with open(Path('./config/base/generate.json'), 'w+') as file:
        current_app.logger.warning("Main configuration settings has been "
                                   "outputted to file: ./config/base/generate.json. "
                                   "Please store this file safely or delete it.")
        json.dump(config_settings, file)
