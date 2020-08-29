import threading
import os
from flask import Blueprint, render_template
from flask_socketio import emit
from pygtail import Pygtail
from queue import Queue

from pygluu.kubernetes.kustomize import Kustomize
from pygluu.kubernetes.helm import Helm
from pygluu.kubernetes.settings import SettingsHandler
from ..extensions import socketio

install_blueprint = Blueprint('install', __name__, template_folder="templates")
settings = SettingsHandler()
timeout = 120
queue = Queue()


@install_blueprint.route('/install')
def install_kustomize():
    t = threading.Thread(target=do_installation, args=(queue,))
    t.daemon = True
    t.start()
    return render_template('install/kustomize.html')


@socketio.on('install', namespace='/test')
def installer_logs():
    data = {}
    tail_log = True
    while tail_log:
        if not queue.empty():
            data = queue.get()

        logs = Pygtail("./setup.log", read_from_end=True, every_n=1)
        for log in logs.readlines():
            emit('response', {'title': data[0], 'log': log, 'status': data[1]})

        if data[1] == 'COMPLETED':
            tail_log = False
            emit('response', {'title': data[0], 'log': 'Installation has been completed', 'status': data[1]})


@socketio.on('disconnect', namespace='/test')
def installation_finish():
    print('Installation completed')


def do_installation(q):
    q.put(('Preparing Installation', 'ONPROGRESS'))
    kustomize = Kustomize(settings.db, timeout)
    kustomize.uninstall()

    if settings.get("INSTALL_REDIS") == "Y" or settings.get("INSTALL_GLUU_GATEWAY") == "Y":
        q.put(('Installing kube-db', 'ONPROGRESS'))
        helm = Helm(settings.db)
        helm.uninstall_kubedb()
        helm.install_kubedb()

    q.put(('Installation in progress', 'ONPROGRESS'))
    kustomize.install()
    q.put(('Installation Completed', 'COMPLETED'))
    os.remove('./setup.log.offset')
