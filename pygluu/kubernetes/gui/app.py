#!/usr/bin/env python

import argparse
import logging
from flask import Flask

from .extensions import csrf, socketio
from .views import wizard
from .install import install
from pygluu.kubernetes.common import copy_templates


def create_app():
    app = Flask(__name__)

    # set app config
    cfg = "pygluu.kubernetes.gui.config.ProductionConfig"
    app.config.from_object(cfg)

    # init csrf
    csrf.init_app(app)
    socketio.init_app(app)

    # register blueprint
    app.register_blueprint(wizard)
    app.register_blueprint(install)

    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", action="store", default="5000")
    parser.add_argument("-d", "--debug", type=bool, action="store",
                        default=False,
                        help="Enable/Disable debug (default: false)")

    args = parser.parse_args()
    port = int(args.port)
    debug = args.debug

    copy_templates()
    app = create_app()
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)
    log.disabled = True
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
