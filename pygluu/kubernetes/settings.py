"""
pygluu.kubernetes.settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with settings saved in a dictionary  for terminal and GUI installations.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import contextlib
import json
import os
import sys
import shutil
import jsonschema
from dotty_dict import dotty
from pygluu.kubernetes.yamlparser import Parser
from pathlib import Path
from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-values-yaml    ")


def unlink_values_yaml():
    filename = Path("./helm/gluu/values.yaml")
    with contextlib.suppress(FileNotFoundError):
        os.unlink(filename)


class ValuesHandler(object):
    def __init__(self, values_file="./helm/gluu/values.yaml", values_schema_file="./helm/gluu/values.schema.json"):
        self.values_file = Path(values_file)
        self.values_schema = Path(values_schema_file)
        self.errors = list()
        self.values_file_parser = Parser(self.values_file, True)
        self.schema = {}
        self.load()

    def load(self):
        """
        Get merged settings (default and custom settings from json file).
        """
        # Check if running in container and settings.json mounted
        try:
            shutil.copy(Path("./override-values.yaml"), self.values_file)
            self.values_file_parser = Parser(self.values_file, True)
        except FileNotFoundError:
            # No installation settings mounted as /override-values.yaml. Checking values.yaml.
            pass

    def store_data(self):
        try:
            self.values_file_parser.dump_it()
            return True
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def set(self, keys_string, value):
        """
        single update
        """
        try:
            dot = dotty(self.values_file_parser)
            dot[keys_string] = value
            self.store_data()
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def get(self, keys_string):
        """
        This method receives a dict and list of attributes to return the innermost value of the give dict
        """
        try:
            dot = dotty(self.values_file_parser)
            return dot[keys_string]

        except (KeyError, NameError):
            logger.info("No Value Can Be Found for " + str(keys_string))
            return False

    def update(self, collection):
        """
        mass update
        """
        try:
            self.values_file_parser.update(collection)
            self.store_data()
            return True
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def reset_data(self):
        """
        reset settings.json to default_settings
        """

        def iterate_dict(dictionary):
            for k, v in dictionary.items():
                if isinstance(v, dict):
                    iterate_dict(v)
                else:
                    dictionary[k] = ""

        try:
            iterate_dict(self.values_file_parser)
            self.store_data()
            return True
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

