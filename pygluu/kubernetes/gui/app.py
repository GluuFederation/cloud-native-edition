import contextlib
import os
import re
import secrets
import shutil
from pathlib import Path

from flask import Flask

from pygluu.kubernetes.gui.extensions import csrf, socketio, gluu_settings
from pygluu.kubernetes.gui.views.main import main_blueprint
from pygluu.kubernetes.gui.views.wizard import wizard_blueprint
from pygluu.kubernetes.gui.views.operation import operation_blueprint


def resolve_secret_key(path):
    key = ""
    with contextlib.suppress(FileNotFoundError):
        with open(path) as f:
            key = f.read().strip()

    if not key:
        key = secrets.token_urlsafe(32)
        with open(path, "w") as f:
            f.write(key)
    return key


def create_app(debug=False):
    """
    GUI installer app for gluu cloud native

    - set app config
    - initialize extensions
    - registering blueprints
    - generate urls for static files
    """
    app = Flask(__name__)

    # set app config
    cfg = "pygluu.kubernetes.gui.config.ProductionConfig"
    app.config.from_object(cfg)
    app.config["DEBUG"] = debug

    # resolve persistent secret key for production
    secret_key_file = Path("./secret-key.txt").resolve()
    with contextlib.suppress(FileNotFoundError):
        # if running inside container, copy mounted file (if any)
        shutil.copy(
            Path("./installer-secret-key.txt").resolve(),
            secret_key_file,
        )
    app.config["SECRET_KEY"] = resolve_secret_key(secret_key_file)

    # init csrf
    csrf.init_app(app)
    socketio.init_app(app)
    gluu_settings.init_app(app)

    # register blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(wizard_blueprint)
    app.register_blueprint(operation_blueprint, url_prefix="/operations")

    @app.context_processor
    def hash_processor():
        def hashed_url(filepath):
            directory, filename = filepath.rsplit('/')
            name, extension = filename.rsplit(".")
            folder = os.path.join(os.path.sep,
                                  app.root_path, 'static', directory)
            files = os.listdir(folder)
            for f in files:
                regex = name + r"\.[a-z0-9]+\." + extension
                if re.match(regex, f):
                    return os.path.join('/static', directory, f)
            return os.path.join('/static', filepath)

        return dict(hashed_url=hashed_url)

    return app
