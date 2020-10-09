from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from pygluu.kubernetes.settings import SettingsHandler


class GluuSettings(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        self.db = SettingsHandler()

    def init_app(self, app):
        app.extensions = getattr(app, "extensions", {})
        app.extensions["gluu_settings"] = self


csrf = CSRFProtect()
socketio = SocketIO()
gluu_settings = GluuSettings()
