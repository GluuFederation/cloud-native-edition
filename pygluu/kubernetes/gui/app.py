#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from pygluu.kubernetes.common import copy_templates
from .views import wizard


def create_app():
    app = Flask(__name__)

    # set app config
    cfg = "pygluu.kubernetes.gui.config.ProductionConfig"
    app.config.from_object(cfg)

    # init csrf
    csrf = CSRFProtect()
    csrf.init_app(app)

    #register blueprint
    app.register_blueprint(wizard)

    return app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", action="store", default="5000")
    parser.add_argument("-d", "--debug", type=bool, action="store", default=False,
                        help="Enable/Disable debug (default: false)")
    parser.add_argument("-D", "--development", help="use development mode")

    args = parser.parse_args()
    port = int(args.port)
    debug = args.debug
    mode = args.development

    copy_templates()
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    main()