"""
pygluu.kubernetes.gui.views.operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contain gui views as main page of gui installer

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import os
import signal
from flask import Blueprint, jsonify
from pygluu.kubernetes.helpers import get_logger
from flask_socketio import emit
from pygtail import Pygtail
from ..extensions import socketio
from ..installer import InstallHandler

logger = get_logger("gluu-gui        ")
operation_blueprint = Blueprint("operation", __name__, template_folder="templates")

@socketio.on("start_installation", namespace="/installation")
def start_installation(target):
    installer = InstallHandler(target=target)
    if target == "install-no-wait":
        installer.target = "install"
        installer.timeout = 0

    installer.run()

    while installer.thread.is_alive():

        if not installer.queue.empty():
            data = installer.queue.get()

        logs = Pygtail("./setup.log", paranoid=True)
        for log in logs.readlines():
            emit("response", {"title": data[0],
                              "log": log,
                              "status": data[1]})

    if not installer.queue.empty():
        data = installer.queue.get()

    logs = Pygtail("./setup.log", paranoid=True)
    for log in logs.readlines():
        emit("response", {"title": data[0], "log": log, "status": data[1]})


@operation_blueprint.route("/stop", methods=["POST"])
def stop_installation():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({"success": True, "message": "Installation Stopped"})


@socketio.on("disconnect", namespace="/installation")
def installation_finish():
    print("Installation completed")