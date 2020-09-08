"""
pygluu.kubernetes.gui.views.wizard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contain gui views for user's input settings.json

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import ipaddress
import shutil
import json
import base64

from pathlib import Path
from flask import current_app
from flask import Blueprint, jsonify, make_response, render_template, \
    request, redirect, url_for, send_from_directory
from wtforms.validators import InputRequired, Optional, DataRequired
from werkzeug.utils import secure_filename

from pygluu.kubernetes.common import get_supported_versions, \
    exec_cmd, generate_password
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import SettingsHandler

from ..forms.architecture import DeploymentArchForm
from ..forms.backup import CouchbaseBackupForm, LdapBackupForm
from ..forms.cache import CacheTypeForm
from ..forms.configuration import ConfigurationForm
from ..forms.couchbase import CouchbaseForm, CouchbaseCalculatorForm, CouchbaseMultiClusterForm
from ..forms.environment import EnvironmentForm
from ..forms.gluugateway import GluuGatewayForm
from ..forms.helpers import volume_types
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


wizard_blueprint = Blueprint('wizard', __name__, template_folder="templates")
wizard_steps = ["License",
                "Gluu version",
                "Deployment architecture",
                "Gluu namespace",
                "Optional Services",
                "Gluu gateway",
                "Install jackrabbit",
                "Install Istio",
                "Environment Setting",
                "Persistence backend",
                "App volumes",
                "Couchbase multi cluster",
                "Cache type",
                "Couchbase",
                "Couchbase calculator",
                "Backup",
                "Config",
                "Image name tag",
                "Replicas"]

kubernetes = Kubernetes()

test_arch = ("microk8s", "minikube")
cloud_arch = ("eks", "gke", "aks", "do")
local_arch = "local"

gluu_cache_map = {
    1: "NATIVE_PERSISTENCE",
    2: "IN_MEMORY",
    3: "REDIS",
}

config_settings = {"hostname": "", "country_code": "", "state": "", "city": "",
                   "admin_pw": "", "ldap_pw": "", "email": "", "org_name": "",
                   "redis_pw": ""}

static_files = ["/favicon.ico",
                "/styles.css",
                "/green-logo.svg",
                "/bootstrap.min.css",
                "/bootstrap.min.css.map"]

settings = SettingsHandler()


@wizard_blueprint.before_request
def initialize():
    """
    check accepting license
    """
    if not settings.get("ACCEPT_GLUU_LICENSE") and request.path != "/license":
        return redirect(url_for("wizard.license"))


@wizard_blueprint.context_processor
def inject_wizard_steps():
    """
    inject wizard_step variable to Jinja
    """
    return dict(wizard_steps=wizard_steps)


@wizard_blueprint.route("/license", methods=["GET", "POST"])
def license():
    """Input for Accepting license
    """
    form = LicenseForm()
    if form.validate_on_submit():
        settings.set("ACCEPT_GLUU_LICENSE", "Y" if form.accept_gluu_license.data else "N")
        return redirect(url_for(request.form["next_step"]))

    with open("./LICENSE", "r") as f:
        agreement_file = f.read()

    if request.method == "GET":
        # populate form data from settings
        form.accept_gluu_license.data = settings.get("ACCEPT_GLUU_LICENSE")

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
    form = VersionForm()
    versions, version_number = get_supported_versions()

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        settings.set("GLUU_VERSION", form.gluu_version.data)
        image_names_and_tags = versions.get(settings.get("GLUU_VERSION"), {})
        settings.update(image_names_and_tags)
        return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form data from settings
        form.gluu_version.data = settings.get("GLUU_VERSION")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=2,
                           template="gluu_version",
                           prev_step="wizard.license",
                           next_step="wizard.deployment_arch")


@wizard_blueprint.route("/deployment-arch", methods=["GET", "POST"])
def deployment_arch():
    """
    Input for the kubernetes infrastructure used.
    """
    form = DeploymentArchForm()

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        settings.set("DEPLOYMENT_ARCH", form.deployment_arch.data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form
        form.deployment_arch.data = settings.get("DEPLOYMENT_ARCH")

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
        settings.set("GLUU_NAMESPACE", form.gluu_namespace.data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        # populate form
        if settings.get("GLUU_NAMESPACE"):
            form.gluu_namespace.data = settings.get("GLUU_NAMESPACE")

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
            'oxauth-key-rotation': False,
            'radius': False,
            'oxpassport': False,
            'oxshibboleth': False,
            'casa': False,
            'fido2': False,
            'scim': False,
            'oxd-server': False
        }
        data["ENABLE_CACHE_REFRESH"] = form.enable_cache_refresh.data
        if data["ENABLE_CACHE_REFRESH"] == "Y":
            service_list['cr-rotate'] = True

        data["ENABLE_OXAUTH_KEY_ROTATE"] = form.enable_oxauth_key_rotate.data
        if data["ENABLE_OXAUTH_KEY_ROTATE"] == "Y":
            data["OXAUTH_KEYS_LIFE"] = form.oxauth_keys_life.data
            service_list['oxauth-key-rotation'] = True
        else:
            data["OXAUTH_KEYS_LIFE"] = ""

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

        data["ENABLE_OXD"] = form.enable_oxd.data

        if data["ENABLE_OXD"] == "Y":
            data["OXD_APPLICATION_KEYSTORE_CN"] = form.oxd_application_keystore_cn.data
            data["OXD_ADMIN_KEYSTORE_CN"] = form.oxd_admin_keystore_cn.data
            service_list['oxd-server'] = True
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

        data["ENABLED_SERVICES_LIST"] = settings.get("ENABLED_SERVICES_LIST")
        for service, stat in service_list.items():
            if stat:
                if service not in data["ENABLED_SERVICES_LIST"]:
                    data["ENABLED_SERVICES_LIST"].append(service)
            else:
                if service in data["ENABLED_SERVICES_LIST"]:
                    data["ENABLED_SERVICES_LIST"].remove(service)

        settings.update(data)
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
        data = {}
        data["INSTALL_GLUU_GATEWAY"] = form.install_gluu_gateway.data

        if data["INSTALL_GLUU_GATEWAY"] == "Y":
            data["ENABLED_SERVICES_LIST"] = settings.get("ENABLED_SERVICES_LIST")
            data["ENABLED_SERVICES_LIST"].append("gluu-gateway-ui")
            data["ENABLE_OXD"] = "Y"
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
            data["ENABLE_OXD"] = "N"
            if not settings.get("POSTGRES_NAMESPACE") and not settings.get("JACKRABBIT_CLUSTER"):
                data["POSTGRES_NAMESPACE"] = ""
            if not settings.get("POSTGRES_REPLICAS") and not settings.get("JACKRABBIT_CLUSTER"):
                data["POSTGRES_REPLICAS"] = ""
            if not settings.get("POSTGRES_URL") and not settings.get("JACKRABBIT_CLUSTER"):
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
        form.postgres = populate_form_data(form.postgres)
        # populate password suggestion
        if not settings.get("KONG_PG_PASSWORD"):
            form.kong_pg_password_confirm.data = form.kong_pg_password.data = generate_password()
        else:
            form.kong_pg_password_confirm.data = settings.get("KONG_PG_PASSWORD")

        if not settings.get("GLUU_GATEWAY_UI_PG_PASSWORD"):
            form.gluu_gateway_ui_pg_password.data = \
                form.gluu_gateway_ui_pg_password_confirm.data = generate_password()
        else:
            form.gluu_gateway_ui_pg_password_confirm.data = settings.get("GLUU_GATEWAY_UI_PG_PASSWORD")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=6,
                           template="gluu_gateway",
                           prev_step="wizard.optional_services",
                           next_step="wizard.install_jackrabbit")


@wizard_blueprint.route("/install-jackrabbit", methods=["GET", "POST"])
def install_jackrabbit():
    """
    Install Jackrabbit
    """
    form = JackrabbitForm()
    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {}
        data["INSTALL_JACKRABBIT"] = form.install_jackrabbit.data
        data["JACKRABBIT_URL"] = form.jackrabbit_url.data
        data["JACKRABBIT_ADMIN_ID"] = form.jackrabbit_admin_id.data
        data["JACKRABBIT_ADMIN_PASSWORD"] = form.jackrabbit_admin_password.data
        data["JACKRABBIT_CLUSTER"] = form.jackrabbit_cluster.data

        if data["INSTALL_JACKRABBIT"] == "Y":
            data["JACKRABBIT_STORAGE_SIZE"] = form.jackrabbit_storage_size.data

        if data["JACKRABBIT_CLUSTER"] == "Y":
            data["POSTGRES_NAMESPACE"] = form.postgres.postgres_namespace.data
            data["POSTGRES_REPLICAS"] = form.postgres.postgres_replicas.data
            data["POSTGRES_URL"] = form.postgres.postgres_url.data
            data["JACKRABBIT_PG_USER"] = form.jackrabbit_pg_user.data
            data["JACKRABBIT_PG_PASSWORD"] = form.jackrabbit_pg_password.data
            data["JACKRABBIT_DATABASE"] = form.jackrabbit_database.data

        settings.update(data)
        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)
        form.postgres = populate_form_data(form.postgres)
        if not settings.get("JACKRABBIT_ADMIN_PASSWORD"):
            form.jackrabbit_admin_password.data = \
                form.jackrabbit_admin_password_confirmation.data = generate_password(24)
        else:
            form.jackrabbit_admin_password.data = \
                form.jackrabbit_admin_password_confirmation.data = settings.get("JACKRABBIT_ADMIN_PASSWORD")

        if not settings.get("JACKRABBIT_PG_PASSWORD"):
            form.jackrabbit_pg_password.data = \
                form.jackrabbit_pg_password_confirmation.data = generate_password()
        else:
            form.jackrabbit_pg_password.data = \
                form.jackrabbit_pg_password_confirmation.data = settings.get("JACKRABBIT_PG_PASSWORD")

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
    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {}
        if settings.get("DEPLOYMENT_ARCH") not in test_arch:
            data["USE_ISTIO_INGRESS"] = form.use_istio_ingress.data
            if data["USE_ISTIO_INGRESS"] == "Y":
                data["ENABLED_SERVICES_LIST"] = settings.get("ENABLED_SERVICES_LIST")
                data["ENABLED_SERVICES_LIST"].append('gluu-istio-ingress')
                data["LB_ADD"] = form.lb_add.data

        data["USE_ISTIO"] = form.use_istio.data
        data["ISTIO_SYSTEM_NAMESPACE"] = form.istio_system_namespace.data

        settings.update(data)
        return redirect(url_for(next_step))

    if settings.get("DEPLOYMENT_ARCH") in test_arch:
        del form.use_istio_ingress
    else:
        form.use_istio_ingress.validators = [DataRequired()]

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
    if form.validate_on_submit():
        data = {}
        next_step = request.form['next_step']

        if not settings.get("TEST_ENVIRONMENT") and \
                settings.get("DEPLOYMENT_ARCH") in test_arch:
            data["TEST_ENVIRONMENT"] = form.test_environment.data

        if settings.get("DEPLOYMENT_ARCH") in cloud_arch or \
                settings.get("DEPLOYMENT_ARCH") in local_arch:
            data["NODE_SSH_KEY"] = form.node_ssh_key.data

        data["HOST_EXT_IP"] = form.host_ext_ip.data

        # prompt AWS
        if settings.get("DEPLOYMENT_ARCH") == "eks":
            data["AWS_LB_TYPE"] = form.aws_lb_type.data
            data["USE_ARN"] = form.use_arn.data
            data["ARN_AWS_IAM"] = form.arn_aws_iam.data

        # prompt GKE
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



@wizard_blueprint.route("/persistence-backend", methods=["GET", "POST"])
def persistence_backend():
    """
    Setup Persistence Backend setting
    """
    form = PersistenceBackendForm()
    if form.validate_on_submit():
        next_step = request.form['next_step']
        data = {}

        data["PERSISTENCE_BACKEND"] = form.persistence_backend.data
        if data["PERSISTENCE_BACKEND"] == "hybrid":
            data["HYBRID_LDAP_HELD_DATA"] = form.hybrid_ldap_held_data.data

        if data["PERSISTENCE_BACKEND"] == "ldap":
            data["ENABLED_SERVICES_LIST"] = settings.get("ENABLED_SERVICES_LIST")
            data["ENABLED_SERVICES_LIST"].append("ldap")

        settings.update(data)

        if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") or \
                settings.get("INSTALL_JACKRABBIT") == "Y":
            if settings.get("DEPLOYMENT_ARCH") == "microk8s":
                settings.set("APP_VOLUME_TYPE", 1)
            elif settings.get("DEPLOYMENT_ARCH") == "minikube":
                settings.set("APP_VOLUME_TYPE", 2)

            if not settings.get("APP_VOLUME_TYPE") \
                    or settings.get("DEPLOYMENT_ARCH") not in test_arch:
                return redirect(url_for('wizard.app_volume_type'))

        if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            return redirect(url_for('wizard.couchbase_multi_cluster'))

        return redirect(url_for(next_step))

    # TODO: find a way to apply dynamic validation
    if settings.get("DEPLOYMENT_ARCH") == "gke":
        form.gmail_account.validators.append(InputRequired())
    else:
        form.gmail_account.validators.append(Optional())

    if request.method == "GET":
        form = populate_form_data(form)

    return render_template("wizard/index.html",
                           settings=settings.db,
                           form=form,
                           current_step=10,
                           template="persistence_backend",
                           prev_step="wizard.environment",
                           next_step="wizard.cache_type")


@wizard_blueprint.route("/app-volume-type", methods=["GET", "POST"])
def app_volume_type():
    """
    App Volume type Setting
    """
    form = VolumeForm()
    if form.validate_on_submit():
        data = {}
        data["APP_VOLUME_TYPE"] = form.app_volume_type.data

        if data["APP_VOLUME_TYPE"] in (8, 13):
            data["LDAP_STATIC_VOLUME_ID"] = form.ldap_static_volume_id.data

        if data["APP_VOLUME_TYPE"] == 18:
            data["LDAP_STATIC_DISK_URI"] = form.ldap_static_disk_uri.data

        if settings.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
            data["LDAP_JACKRABBIT_VOLUME"] = form.ldap_jackrabbit_volume.data

        settings.update(data)

        if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            next_step = "wizard.couchbase_multi_cluster"
        else:
            next_step = request.form['next_step']

        return redirect(url_for(next_step))

    return render_template("wizard/index.html",
                           settings=settings.db,
                           form=form,
                           current_step=11,
                           template="app_volume_type",
                           prev_step="wizard.persistence_backend",
                           next_step="wizard.cache_type")


@wizard_blueprint.route("/couchbase-multi-cluster", methods=["GET", "POST"])
def couchbase_multi_cluster():
    """
    Deploy multi-cluster settings
    """
    form = CouchbaseMultiClusterForm()
    if form.validate_on_submit():
        settings.set("DEPLOY_MULTI_CLUSTER", form.deploy_multi_cluster.data)
        return redirect(url_for(request.form['next_step']))

    if request.method == "GET":
        form = populate_form_data(form)

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.persistence_backend"
    if settings.get("APP_VOLUME_TYPE") not in (1, 2):
        prev_step = "wizard.app_volume_type"

    return render_template("wizard/index.html",
                           form=form,
                           current_step=12,
                           template="couchbase_multi_cluster",
                           prev_step=prev_step,
                           next_step="wizard.cache_type")


@wizard_blueprint.route("/cache-type", methods=["GET", "POST"])
def cache_type():
    """
    Cache Layer setting
    """
    form = CacheTypeForm()
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
            return redirect(url_for('wizard.backup'))

        return redirect(url_for('wizard.config'))

    if request.method == "GET":
        form = populate_form_data(form)
        form.redis = populate_form_data(form.redis)
        form.redis.redis_pw_confirm.data = settings.get("REDIS_PW")

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.persistence_backend"
    if settings.get("APP_VOLUME_TYPE") not in (1, 2):
        prev_step = "wizard.app_volume_type"
    elif settings.get("DEPLOY_MULTI_CLUSTER"):
        prev_step = "wizard.couchbase_multi_cluster"

    return render_template("wizard/index.html",
                           form=form,
                           current_step=13,
                           template="cache_type",
                           prev_step=prev_step,
                           next_step="wizard.couchbase")


@wizard_blueprint.route("/couchbase", methods=["GET", "POST"])
def couchbase():
    form = CouchbaseForm()
    custom_cb_ca_crt = Path("./couchbase_crts_keys/ca.crt")
    custom_cb_crt = Path("./couchbase_crts_keys/chain.pem")
    custom_cb_key = Path("./couchbase_crts_keys/pkey.key")

    if form.validate_on_submit():
        next_step = request.form["next_step"]
        data = {}
        data["INSTALL_COUCHBASE"] = form.install_couchbase.data
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

        if settings.get("DEPLOYMENT_ARCH") in test_arch:
            data["COUCHBASE_USE_LOW_RESOURCES"] = "Y"
        else:
            data["COUCHBASE_USE_LOW_RESOURCES"] = form.couchbase_use_low_resources.data

        data["COUCHBASE_NAMESPACE"] = form.couchbase_namespace.data
        data["COUCHBASE_CLUSTER_NAME"] = form.couchbase_cluster_name.data
        data["COUCHBASE_URL"] = form.couchbase_url.data
        data["COUCHBASE_USER"] = form.couchbase_user.data
        data["COUCHBASE_PASSWORD"] = form.couchbase_password.data

        if not custom_cb_ca_crt.exists() or\
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

        settings.update(data)

        if settings.get("COUCHBASE_USE_LOW_RESOURCES") == "N" and \
                settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "N" and \
                settings.get("INSTALL_COUCHBASE") == "Y":
            return redirect(url_for("wizard.couchbase_calculator"))

        if settings.get("DEPLOYMENT_ARCH") not in test_arch:
            return redirect(url_for("wizard.backup"))

        return redirect(url_for(next_step))

    if request.method == "GET":
        form = populate_form_data(form)

        if not settings.get("COUCHBASE_PASSWORD"):
            form.couchbase_password.data = \
                form.couchbase_password_confirmation.data = generate_password()
        else:
            form.couchbase_password_confirmation.data = settings.get("COUCHBASE_PASSWORD")

        if settings.get("DEPLOYMENT_ARCH") in test_arch:
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
                           current_step=14,
                           template="couchbase",
                           prev_step="wizard.couchbase_multi_cluster",
                           next_step="wizard.config")


@wizard_blueprint.route("/couchbase-calculator", methods=["GET", "POST"])
def couchbase_calculator():
    """
    Attempt to Calculate resources needed
    """

    form = CouchbaseCalculatorForm()

    if form.validate_on_submit():
        data = {}
        for field in form:
            if field.name == "csrf_token":
                continue
            data[field.name.upper()] = field.data

        settings.update(data)

        if settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            return redirect(url_for("wizard.backup"))

        return redirect(url_for(request.form["next_step"]))

    if settings.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke") and \
            not settings.get("COUCHBASE_VOLUME_TYPE"):
        volume_type = volume_types[settings.get("DEPLOYMENT_ARCH")]
        form.couchbase_volume_type.choices = volume_type["choices"]
        form.couchbase_volume_type.validators = [DataRequired()]

    return render_template("wizard/index.html",
                           form=form,
                           current_step=15,
                           template="couchbase_calculator",
                           prev_step="wizard.couchbase",
                           next_step="wizard.config")


@wizard_blueprint.route("/backup", methods=["GET", "POST"])
def backup():
    if not settings.get("PERSISTENCE_BACKEND"):
        return redirect(url_for('wizard.setting'))

    if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
        form = CouchbaseBackupForm()
    elif settings.get("PERSISTENCE_BACKEND") == "ldap":
        form = LdapBackupForm()

    if form.validate_on_submit():
        data = {}
        if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            data["COUCHBASE_INCR_BACKUP_SCHEDULE"] = form.couchbase_incr_backup_schedule.data
            data["COUCHBASE_FULL_BACKUP_SCHEDULE"] = form.couchbase_full_backup_schedule.data
            data["COUCHBASE_BACKUP_RETENTION_TIME"] = form.couchbase_backup_retention_time.data
            data["COUCHBASE_BACKUP_STORAGE_SIZE"] = form.couchbase_backup_storage_size.data
        elif settings.get("PERSISTENCE_BACKEND") == "ldap":
            data["LDAP_BACKUP_SCHEDULE"] = form.ldap_backup_schedule.data

        settings.update(data)
        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.setting"
    if settings.get("APP_VOLUME_TYPE") not in (1, 2):
        prev_step = "wizard.app_volume_type"
    elif settings.get("DEPLOY_MULTI_CLUSTER"):
        prev_step = "wizard.couchbase_multi_cluster"
    elif settings.get("INSTALL_COUCHBASE"):
        prev_step = "wizard.couchbase"
    elif settings.get("NUMBER_OF_EXPECTED_USERS"):
        prev_step = "wizard.couchbase_calculator"

    return render_template("wizard/index.html",
                           persistence_backend=settings.get("PERSISTENCE_BACKEND"),
                           form=form,
                           current_step=16,
                           template="backup",
                           prev_step=prev_step,
                           next_step="wizard.config")


@wizard_blueprint.route("/config", methods=["GET", "POST"])
def config():
    form = ConfigurationForm()
    if form.validate_on_submit():
        data = {}
        data["GLUU_FQDN"] = form.gluu_fqdn.data
        data["COUNTRY_CODE"] = form.country_code.data
        data["STATE"] = form.state.data
        data["CITY"] = form.city.data
        data["EMAIL"] = form.email.data
        data["ORG_NAME"] = form.org_name.data
        data["ADMIN_PW"] = form.admin_pw.data

        if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
            data["LDAP_PW"] = form.ldap_pw.data
        else:
            data["LDAP_PW"] = settings.get("COUCHBASE_PASSWORD")

        if settings.get("DEPLOYMENT_ARCH") in test_arch:
            data["IS_GLUU_FQDN_REGISTERED"] = "N"
        else:
            data["IS_GLUU_FQDN_REGISTERED"] = form.is_gluu_fqdn_registered.data

        if data["IS_GLUU_FQDN_REGISTERED"] == "N":
            data["ENABLED_SERVICES_LIST"] = settings.get("ENABLED_SERVICES_LIST")
            data["ENABLED_SERVICES_LIST"].append("update-lb-ip")
        settings.update(data)
        generate_main_config()

        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)
        if not settings.get("ADMIN_PW"):
            form.admin_pw.data = form.admin_pw_confirm.data = generate_password()
        else:
            form.admin_pw_confirm.data = settings.get("ADMIN_PW")

        if not settings.get("LDAP_PW"):
            form.ldap_pw.data = form.ldap_pw_confirm.data = generate_password()
        else:
            form.ldap_pw_confirm.data = settings.get("LDAP_PW")

        if settings.get("DEPLOYMENT_ARCH") in test_arch:
            form.is_gluu_fqdn_registered.validators = [Optional()]
            form.is_gluu_fqdn_registered.data = "N"
        else:
            form.is_gluu_fqdn_registered.validators = [DataRequired()]

    # TODO: find a way to get better work on dynamic wizard step
    prev_step = "wizard.persistence_backend"
    if settings.get("APP_VOLUME_TYPE") not in (1, 2):
        prev_step = "wizard.app_volume_type"
    elif settings.get("DEPLOY_MULTI_CLUSTER"):
        prev_step = "wizard.couchbase_multi_cluster"
    elif settings.get("INSTALL_COUCHBASE"):
        prev_step = "wizard.couchbase"
    elif settings.get("NUMBER_OF_EXPECTED_USERS"):
        prev_step = "wizard.couchbase_calculator"
    elif settings.get("COUCHBASE_INCR_BACKUP_SCHEDULE") or settings.get("LDAP_BACKUP_SCHEDULE"):
        prev_step = "wizard.backup"

    return render_template("wizard/index.html",
                           settings=settings.db,
                           form=form,
                           current_step=17,
                           template="config",
                           prev_step=prev_step,
                           next_step="wizard.image_name_tag")


@wizard_blueprint.route("/image-name-tag", methods=["POST", "GET"])
def image_name_tag():
    form = ImageNameTagForm()
    if form.validate_on_submit():
        data = {}
        for field in form:
            if field.name == "csrf_token":
                continue
            data[field.name.upper()] = field.data
        data["EDIT_IMAGE_NAMES_TAGS"] = "N"
        settings.update(data)

        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        form = populate_form_data(form)
        if settings.get("ENABLE_CASA") == "N":
            del form.casa_image_name
            del form.casa_image_tag
        if settings.get("ENABLE_CACHE_REFRESH") == "N":
            del form.cache_refresh_rotate_image_name
            del form.cache_refresh_rotate_image_tag
        if settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "N":
            del form.cert_manager_image_name
            del form.cert_manager_image_tag
        if settings.get("PERSISTENCE_BACKEND") not in ("hybrid", "ldap"):
            del form.ldap_image_name
            del form.ldap_image_tag
        if settings.get("ENABLE_OXD") == "N":
            del form.oxd_image_name
            del form.oxd_image_tag
        if settings.get("ENABLE_OXPASSPORT") == "N":
            del form.oxpassport_image_name
            del form.oxpassport_image_tag
        if settings.get("ENABLE_OXSHIBBOLETH") == "N":
            del form.oxshibboleth_image_name
            del form.oxshibboleth_image_tag
        if settings.get("ENABLE_RADIUS") == "N":
            del form.radius_image_name
            del form.radius_image_tag
        if settings.get("INSTALL_GLUU_GATEWAY") == "N":
            del form.gluu_gateway_image_name
            del form.gluu_gateway_image_tag
            del form.gluu_gateway_ui_image_name
            del form.gluu_gateway_ui_image_tag

    return render_template("wizard/index.html",
                           form=form,
                           current_step=18,
                           template="image_name_tag",
                           prev_step="wizard.config",
                           next_step="wizard.replicas")


@wizard_blueprint.route("/replicas", methods=["POST", "GET"])
def replicas():
    form = ReplicasForm()

    if form.validate_on_submit():
        data = {}
        for field in form:
            if field.name == "csrf_token":
                continue
            data[field.name.upper()] = field.data

        settings.update(data)

        if settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and \
                not settings.get("LDAP_STORAGE_SIZE"):
            return redirect(url_for(request.form["next_step"]))

        return redirect(url_for("wizard.setting_summary"))

    if request.method == "GET":
        form = populate_form_data(form)
        if settings.get("ENABLE_FIDO2") == "N":
            del form.fido2_replicas
        if settings.get("ENABLE_SCIM") == "N":
            del form.scim_replicas
        if settings.get("PERSISTENCE_BACKEND") not in ("hybrid", "ldap"):
            del form.ldap_replicas
        if settings.get("ENABLE_OXSHIBBOLETH") == "N":
            del form.oxshibboleth_replicas
        if settings.get("ENABLE_OXPASSPORT") == "N":
            del form.oxpassport_replicas
        if settings.get("ENABLE_OXD") == "N":
            del form.oxd_server_replicas
        if settings.get("ENABLE_CASA") == "N":
            del form.casa_replicas
        if settings.get("ENABLE_RADIUS") == "N":
            del form.radius_replicas

    return render_template("wizard/index.html",
                           form=form,
                           current_step=19,
                           template="replicas",
                           prev_step="wizard.image_name_tag",
                           next_step="wizard.storage")


@wizard_blueprint.route("/storage", methods=["POST", "GET"])
def storage():
    form = StorageForm()
    if form.validate_on_submit():
        settings.set("LDAP_STORAGE_SIZE", form.ldap_storage_size.data)
        return redirect(url_for(request.form["next_step"]))

    if request.method == "GET":
        if settings.get("LDAP_STORAGE_SIZE"):
            form.ldap_storage_size.data = settings.get("LDAP_STORAGE_SIZE")

    return render_template("wizard/index.html",
                           form=form,
                           current_step=19,
                           template="storage",
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
                       "GLUU_GATEWAY_UI_PG_PASSWORD"]

    return render_template("wizard/setting_summary.html",
                           hidden_settings=hidden_settings,
                           settings=settings.db)


@wizard_blueprint.route("/confirm-params", methods=["POST"])
def confirm_params():
    """
    Display all data from settings.json except for passwords.
    """
    settings.set("CONFIRM_PARAMS", request.form["confirm_params"])
    if settings.get("CONFIRM_PARAMS") == "Y":
        return redirect(url_for('wizard.finished'))
    else:
        # reset to default settings
        settings.reset_data()
        return redirect(url_for('wizard.license'))


@wizard_blueprint.route("/finish")
def finished():
    """
    finish page
    """
    return render_template("wizard/finish.html")


@wizard_blueprint.route("/determine_ip", methods=["GET"])
def determine_ip():
    """
    Attempts to detect and return ip automatically.
    Also set node names, zones, and addresses in a cloud deployment.
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
                if settings.get("DEPLOYMENT_ARCH") != "do" or \
                        settings.get("DEPLOYMENT_ARCH") != "local":
                    node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                    node_zone_list.append(node_zone)
                node_name_list.append(node_name)

        settings.set("NODES_NAMES", node_name_list)
        settings.set("NODES_ZONES", node_zone_list)
        settings.set("NODES_IPS", node_ip_list)

        if settings.get("DEPLOYMENT_ARCH") in ["eks", "gke", "do", "local", "aks"]:
            #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
            ip = "22.22.22.22"
        data = {"status": True,
                'ip_address': ip,
                "message": "Is this the correct external IP address?"}
    except Exception as e:
        current_app.logger.error(e)
        # prompt for user-inputted IP address
        current_app.logger.warning("Cannot determine IP address")
        data = {"status": False, 'message': "Cannot determine IP address"}

    return make_response(jsonify(data), 200)


def populate_form_data(form):
    """
    populate form data from settings
    """
    for k, v in form.data.items():
        if k == "csrf_token":
            continue

        value = settings.get(k.upper())
        if value:
            form[k].data = value
    return form


def generate_main_config():
    """
    Prepare generate.json and output it
    """
    config_settings["hostname"] = settings.get("GLUU_FQDN")
    config_settings["country_code"] = settings.get("COUNTRY_CODE")
    config_settings["state"] = settings.get("STATE")
    config_settings["city"] = settings.get("CITY")
    config_settings["admin_pw"] = settings.get("ADMIN_PW")
    config_settings["ldap_pw"] = settings.get("LDAP_PW")
    config_settings["redis_pw"] = settings.get("REDIS_PW")
    if settings.get("PERSISTENCE_BACKEND") == "couchbase":
        config_settings["ldap_pw"] = settings.get("COUCHBASE_PASSWORD")
    config_settings["email"] = settings.get("EMAIL")
    config_settings["org_name"] = settings.get("ORG_NAME")

    with open(Path('./config/base/generate.json'), 'w+') as file:
        current_app.logger.warning("Main configuration settings has been "
                           "outputted to file: ./config/base/generate.json. "
                           "Please store this file safely or delete it.")
        json.dump(config_settings, file)
