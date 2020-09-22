from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_socketio import emit
from pygtail import Pygtail
from pygluu.kubernetes.settings import SettingsHandler
from ..installer import InstallHandler
from ..extensions import socketio
from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-gui        ")
main_blueprint = Blueprint("main", __name__, template_folder="templates")

settings = SettingsHandler()
installer = InstallHandler()


@main_blueprint.route("/")
def index():
    return render_template("index.html")


@main_blueprint.route("/install", methods=["GET", "POST"])
def install():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "install"
            installer.run_install()

            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"
    if settings.is_exist() and not settings.get('ACCEPT_GLUU_LICENSE'):
        return redirect(url_for("wizard.license"))
    else:
        return redirect(url_for("wizard.setting_summary"))


@main_blueprint.route("/install-no-wait", methods=["GET", "POST"])
def install_no_wait():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.timeout = 0
            installer.target = "install"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"
    if settings.is_exist() and not settings.get('ACCEPT_GLUU_LICENSE'):
        return redirect(url_for("wizard.license"))
    else:
        return redirect(url_for("wizard.setting_summary"))


@main_blueprint.route("/install-ldap-backup", methods=["GET", "POST"])
def install_ldap_backup():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "install-ldap-backup"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"
    if settings.is_exist() and not settings.get('ACCEPT_GLUU_LICENSE'):
        return redirect(url_for("wizard.license"))
    else:
        return redirect(url_for("wizard.setting_summary"))


@main_blueprint.route("/install-kubedb", methods=["GET", "POST"])
def install_kubedb():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "install-kubedb"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"

    # validating settings.json
    if settings.is_exist() and not settings.get('ACCEPT_GLUU_LICENSE'):
        return redirect(url_for("wizard.license"))
    else:
        return redirect(url_for("wizard.setting_summary"))


@main_blueprint.route("/install-gg-dbmode", methods=["GET", "POST"])
def install_gg_dbmode():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "install-gg-dbmode"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"

    # validating settings.json
    if settings.is_exist() and not settings.get('ACCEPT_GLUU_LICENSE'):
        return redirect(url_for("wizard.license"))
    else:
        if validating_gg_settings():
            return redirect(url_for("wizard.setting_summary"))
        else:
            return redirect(url_for("wizard.gluu_gateway"))


@main_blueprint.route("/install-couchbase", methods=["GET", "POST"])
def install_couchbase():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "install-couchbase"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/install-couchbase-backup", methods=["GET", "POST"])
def install_couchbase_backup():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "install-couchbase-backup"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "kustomize"
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/helm-install-gg-dbmode", methods=["GET", "POST"])
def helm_install_gg_dbmode():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "helm-install-gg-dbmode"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "helm"
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/helm-install", methods=["GET", "POST"])
def helm_install():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "helm-install"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "helm"
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/helm-install-gluu", methods=["GET", "POST"])
def helm_install_gluu():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "helm-install-gluu"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    session["install_method"] = "helm"
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/generate-settings", methods=["GET", "POST"])
def generate_settings():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            return redirect(url_for("main.index"))
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/upgrade", methods=["GET", "POST"])
def upgrade():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "upgrade"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/restore", methods=["GET", "POST"])
def restore():
    if request.method == "POST":
        if request.form["install_confirm"] == "Y":
            installer.target = "restore"
            installer.run_install()
            return render_template("install/kustomize.html")
        else:
            settings.reset_data()
            return redirect(url_for("main.index"))

    session["finish_endpoint"] = request.endpoint
    return redirect(url_for("wizard.license"))


@main_blueprint.route("/uninstall", methods=["POST"])
def uninstall():
    if request.method == "POST":
        if request.form["uninstall_confirm"] == "Y":
            installer.target = request.form["target"]
            installer.run_uninstall()
            return render_template("install/kustomize.html")


@socketio.on("install", namespace="/logs")
def installer_logs():
    data = ("Installation in progress", "ONPROGRESS")
    while installer.thread.is_alive():

        if not installer.queue.empty():
            data = installer.queue.get()

        logs = Pygtail("./setup.log", paranoid=True)
        for log in logs.readlines():
            if data[0] == "ERROR":
                emit("response", {"title": data[0], "log": data[1], "status": data[0]})
            else:
                emit("response", {"title": data[0], "log": log, "status": data[1]})

    if not installer.queue.empty():
        data = installer.queue.get()

    emit("response", {"title": data[0], "status": data[1]})


@socketio.on("disconnect", namespace="/logs")
def installation_finish():
    print("Installation completed")


def validating_gg_settings():
    status = True
    keys = [
        "INSTALL_GLUU_GATEWAY",
        "ENABLED_SERVICES_LIST",
        "ENABLE_OXD",
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
            if not settings.get("INSTALL_GLUU_GATEWAY") or \
                    settings.get("INSTALL_GLUU_GATEWAY") == "N":
                status = False
                break

        if settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            if key == "ENABLED_SERVICES_LIST":
                enable_services = settings.get("ENABLED_SERVICES_LIST")
                if "gluu-gateway-ui" not in enable_services:
                    status = False
                    break

            if key == "ENABLE_OXD" and settings.get("ENABLE_OXD") == "N":
                status = False
                break

            if not settings.get(key):
                status = False
                break
    return status
