import os
import re

from flask import Flask

from pygluu.kubernetes.gui.extensions import csrf, socketio
from pygluu.kubernetes.gui.views.main import main_blueprint
from pygluu.kubernetes.gui.views.wizard import wizard_blueprint


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

    # init csrf
    csrf.init_app(app)
    socketio.init_app(app)

    # register blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(wizard_blueprint)

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
