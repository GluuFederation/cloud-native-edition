from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from pygluu.kubernetes.settings import SettingsHandler


class GluuSettings(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.db = SettingsHandler()
        app.gluu_settings = self


csrf = CSRFProtect()
socketio = SocketIO()
gluu_settings = GluuSettings()
