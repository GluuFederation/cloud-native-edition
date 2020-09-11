from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_socketio import emit
from pygtail import Pygtail
from pygluu.kubernetes.settings import SettingsHandler
from ..installer import InstallHandler
from ..extensions import socketio

main_blueprint = Blueprint('main', __name__, template_folder="templates")
settings = SettingsHandler()
installer = InstallHandler()


@main_blueprint.route('/')
def index():
    return render_template('index.html')


@main_blueprint.route('/install', methods=['GET', 'POST'])
def install():
    if request.method == 'POST':
        if request.form['install_confirm'] == "Y":
            installer.run_install_kustomize()
            return render_template('install/kustomize.html')
        else:
            settings.reset_data()
            return redirect(url_for('main.index'))

    session['finish_endpoint'] = request.endpoint
    return redirect(url_for('wizard.license'))


@main_blueprint.route('/install-no-wait', methods=['GET', 'POST'])
def install_no_wait():
    if request.method == 'POST':
        if request.form['install_confirm'] == "Y":
            installer.timeout = 0
            installer.run_install_kustomize()
            return render_template('install/kustomize.html')
        else:
            settings.reset_data()
            return redirect(url_for('main.index'))

    session['finish_endpoint'] = request.endpoint
    return redirect(url_for('wizard.license'))


@main_blueprint.route('/generate-settings', methods=['GET', 'POST'])
def generate_settings():
    if request.method == 'POST':
        if request.form['install_confirm'] == "Y":
            return redirect(url_for('main.index'))
        else:
            settings.reset_data()
            return redirect(url_for('main.index'))

    session['finish_endpoint'] = request.endpoint
    return redirect(url_for('wizard.license'))

@socketio.on('install', namespace='/test')
def installer_logs():
    data = {}
    tail_log = True
    while tail_log:
        if not installer.queue.empty():
            data = installer.queue.get()

        logs = Pygtail("./setup.log", read_from_end=True, every_n=1)
        for log in logs.readlines():
            emit('response', {'title': data[0], 'log': log, 'status': data[1]})

        if data[1] == 'COMPLETED':
            tail_log = False
            emit('response', {'title': data[0], 'log': 'Installation has been completed', 'status': data[1]})


@socketio.on('disconnect', namespace='/test')
def installation_finish():
    print('Installation completed')
