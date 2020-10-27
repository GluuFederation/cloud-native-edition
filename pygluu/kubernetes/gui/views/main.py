"""
pygluu.kubernetes.gui.views.main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contain gui views as main page of gui installer

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import os
from flask import Blueprint, render_template, \
    redirect, url_for, request, session, \
    current_app, jsonify
from flask_socketio import emit
from pygtail import Pygtail
from werkzeug.utils import secure_filename
from ..extensions import socketio
from ..extensions import gluu_settings
from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-gui        ")
main_blueprint = Blueprint("main", __name__, template_folder="templates")


@main_blueprint.route("/")
def index():
    return render_template("index.html")


@main_blueprint.route("/install", methods=["GET", "POST"])
def install():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/install-no-wait", methods=["GET", "POST"])
def install_no_wait():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install-no-wait")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/install-ldap-backup", methods=["GET", "POST"])
def install_ldap_backup():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install-ldap-backup")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/install-kubedb", methods=["GET", "POST"])
def install_kubedb():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install-kubedb")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/install-gg-dbmode", methods=["GET", "POST"])
def install_gg_dbmode():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install-gg-dbmode")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint

    if validating_gg_settings():
        return render_template("preinstall.html",
                               title="Setup install Settings",
                               setting_exist=gluu_settings.db.is_exist())
    else:
        return redirect(url_for("wizard.gluu_gateway"))


@main_blueprint.route("/install-couchbase", methods=["GET", "POST"])
def install_couchbase():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install-couchbase")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/install-couchbase-backup", methods=["GET", "POST"])
def install_couchbase_backup():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="install-couchbase-backup")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/helm-install-gg-dbmode", methods=["GET", "POST"])
def helm_install_gg_dbmode():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="helm-install-gg-dbmode")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/helm-install", methods=["GET", "POST"])
def helm_install():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="helm-install")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/helm-install-gluu", methods=["GET", "POST"])
def helm_install_gluu():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="helm-install-gluu")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup install Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/generate-settings", methods=["GET", "POST"])
def generate_settings():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return redirect(url_for("main.index"))
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return redirect(url_for("wizard.agreement"))


@main_blueprint.route("/upgrade", methods=["GET", "POST"])
def upgrade():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="upgrade")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup upgrade Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/restore", methods=["GET", "POST"])
def restore():
    if request.method == "POST":
        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            return render_template("installation.html", target="restore")
        else:
            gluu_settings.db.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return render_template("preinstall.html",
                           title="Setup restore Settings",
                           setting_exist=gluu_settings.db.is_exist())


@main_blueprint.route("/uninstall", methods=["POST"])
def uninstall():
    if request.method == "POST":
        uninstall_confirm = request.form.get("uninstall_confirm", None)

        if uninstall_confirm == "Y":
            session["installer_target"] = request.form.get("target", None)
            session["finish_endpoint"] = request.endpoint
            settings_exist = gluu_settings.db.is_exist()
            if settings_exist:
                redirect_url = get_wizard_step()
                return redirect(redirect_url)
            else:
                return render_template("preinstall.html",
                                       title="Setup Uninstall Settings",
                                       setting_exist=settings_exist)

        if request.form["confirm_params"] == "Y":
            gluu_settings.db.set("CONFIRM_PARAMS", "Y")
            target = session["installer_target"]
            return render_template("installation.html", target=target)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@main_blueprint.route('/upload-settings', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"success": False, 'message': 'No file uploaded'})
        file = request.files['file']

        if file.filename == '':
            return jsonify({"success": False, 'message': 'No file uploaded'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('./', filename))
            redirect_url = get_wizard_step()
            return jsonify({"success": True,
                            'message': 'File settings has been uploaded',
                            "redirect_url": redirect_url})
        else:
            return jsonify({"success": False, 'message': 'File type not supported'})


def validating_gg_settings():
    status = True
    keys = [
        "INSTALL_GLUU_GATEWAY",
        "ENABLED_SERVICES_LIST",
        "ENABLE_CLIENT_API",
        "POSTGRES_NAMESPACE",
        "POSTGRES_REPLICAS",
        "POSTGRES_URL",
        "KONG_NAMESPACE",
        "GLUU_GATEWAY_UI_NAMESPACE",
        "KONG_PG_USER",
        "KONG_PG_PASSWORD",
        "GLUU_GATEWAY_UI_PG_USER",
        "GLUU_GATEWAY_UI_PG_PASSWORD",
        "KONG_DATABASE",
        "GLUU_GATEWAY_UI_DATABASE"
    ]

    for key in keys:
        if key == "INSTALL_GLUU_GATEWAY":
            if not gluu_settings.db.get("INSTALL_GLUU_GATEWAY") or \
                    gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "N":
                status = False
                break

        if gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "Y":
            if key == "ENABLED_SERVICES_LIST":
                enable_services = gluu_settings.db.get("ENABLED_SERVICES_LIST")
                if "gluu-gateway-ui" not in enable_services:
                    status = False
                    break

            if key == "ENABLE_CLIENT_API" and gluu_settings.db.get("ENABLE_CLIENT_API") == "N":
                status = False
                break

            if not gluu_settings.db.get(key):
                status = False
                break
    return status


def get_wizard_step():
    """
    Define wizard step based on settings value
    :return:
    """
    if not gluu_settings.db.get("ACCEPT_CN_LICENSE"):
        return url_for("wizard.agreement")

    if not gluu_settings.db.get("CN_VERSION"):
        return url_for("wizard.gluu_version")

    if not gluu_settings.db.get("DEPLOYMENT_ARCH"):
        return url_for("wizard.deployment_arch")

    if not gluu_settings.db.get("CN_NAMESPACE"):
        return url_for("wizard.gluu_namespace")

    if not gluu_settings.db.get("ENABLE_CACHE_REFRESH"):
        return url_for("wizard.optional_services")

    if not gluu_settings.db.get("INSTALL_GLUU_GATEWAY"):
        return url_for("wizard.gluu_gateway")

    if gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "Y" and \
            gluu_settings.db.get("KONG_PG_PASSWORD"):
        return url_for("wizard.gluu_gateway")

    if not gluu_settings.db.get("INSTALL_JACKRABBIT"):
        return url_for("wizard.install_jackrabbit")

    if not gluu_settings.db.get("USE_ISTIO"):
        return url_for("wizard.install_istio")

    if not gluu_settings.db.get("HOST_EXT_IP"):
        return url_for("wizard.environment")

    if not gluu_settings.db.get("PERSISTENCE_BACKEND"):
        return url_for("wizard.persistence_backend")

    if not gluu_settings.db.get("APP_VOLUME_TYPE"):
        return url_for("wizard.volumes")

    if not gluu_settings.db.get("INSTALL_COUCHBASE") and \
            gluu_settings.db.get("PERSISTENCE_BACKEND") == "couchbase":
        return url_for("wizard.couchbase")

    if not gluu_settings.db.get("CN_CACHE_TYPE"):
        return url_for("wizard.cache_type")

    if gluu_settings.db.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube") and \
            gluu_settings.db.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase") and \
            not gluu_settings.db.get("COUCHBASE_INCR_BACKUP_SCHEDULE"):
        return url_for("wizard.backup")
    elif gluu_settings.db.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube") and \
            gluu_settings.db.get("PERSISTENCE_BACKEND") == "ldap" and \
            not gluu_settings.db.get("LDAP_BACKUP_SCHEDULE"):
        return url_for("wizard.backup")

    if not gluu_settings.db.get("CN_FQDN"):
        return url_for("wizard.configuration")

    if not gluu_settings.db.get("EDIT_IMAGE_NAMES_TAGS"):
        return url_for("wizard.images")

    if not gluu_settings.db.get("AUTH_SERVER_REPLICAS"):
        return url_for("wizard.replicas")

    return url_for("wizard.setting_summary")