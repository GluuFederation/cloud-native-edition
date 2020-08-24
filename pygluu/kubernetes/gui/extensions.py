from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

csrf = CSRFProtect()
socketio = SocketIO()
