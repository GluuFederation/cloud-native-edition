from gevent import monkey
monkey.patch_all()

import argparse
import logging

from gunicorn.app.base import BaseApplication
from werkzeug.debug import DebuggedApplication

from pygluu.kubernetes.helpers import copy_templates


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


class GluuApp(BaseApplication):
    """Custom Gunicorn-based app.
    """

    def __init__(self, options=None):
        self.options = options or {}
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        from pygluu.kubernetes.gui.app import create_app

        debug = self.options.get("reload") or False
        app = create_app(debug)

        app.logger.disabled = True
        logging.getLogger('werkzeug').disabled = True
        logging.getLogger('socketio').setLevel(logging.ERROR)
        logging.getLogger('engineio').setLevel(logging.ERROR)

        if app.debug:
            # enable pretty debug on web UI
            app = DebuggedApplication(app, evalex=False)
        return app


def run():
    args = parse_args()

    # copy required templates to current directory
    copy_templates()

    options = {
        "bind": f"{args.host}:{args.port}",
        "worker_class": "gevent",
        "reload": args.debug,
    }
    GluuApp(options).run()
