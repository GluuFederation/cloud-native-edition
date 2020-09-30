from gevent import monkey
monkey.patch_all()

import argparse
import logging
import os
import re
from flask import Flask
import gunicorn.app.base
from werkzeug.debug import DebuggedApplication

from .extensions import csrf, socketio
from pygluu.kubernetes.gui.views.main import main_blueprint
from pygluu.kubernetes.gui.views.wizard import wizard_blueprint
from pygluu.kubernetes.helpers import copy_templates


class GluuApp(gunicorn.app.base.BaseApplication):
    """
    Gunicorn app initialization
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def create_app():
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


def parse_args(args=None):
    """Parse arguments.

    Arguments :
        -H --host : define hostname
        -p --port : define port
        -d --debug : override debug value default is False

    :param args:
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default="0.0.0.0",
                        help="The interface to bind to (default to %(default)s)")
    parser.add_argument("-p", "--port", type=int, default=5000,
                        help="The port to bind to (default to %(default)d)")
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debug mode")
    return parser.parse_args(args)


def main():
    """
    App initialization with parser to handle argument from CLI

    Note :
        web logs and socketio is disabled to avoid mixing with system logs
        this make easier to read system logs.
    """
    args = parse_args()
    copy_templates()
    app = create_app()

    app.logger.disabled = True
    logging.getLogger('werkzeug').disabled = True
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

    if args.debug:
        app.config.update(DEBUG=args.debug)
        app = DebuggedApplication(app, evalex=False)

    options = {
        'bind': '%s:%s' % (args.host, args.port),
        'worker_class': 'gevent',
        'reload': args.debug
    }

    GluuApp(app, options).run()


if __name__ == "__main__":
    main()
