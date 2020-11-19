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
from pathlib import Path
from pygluu.kubernetes.helpers import get_logger, update_settings_json_file

logger = get_logger("gluu-setting        ")


def unlink_settings_json():
    filename = Path("./settings.json")
    with contextlib.suppress(FileNotFoundError):
        os.unlink(filename)


class SettingsHandler(object):
    def __init__(self):
        self.setting_file = Path("./settings.json")
        self.setting_schema = Path("./settings_schema.json")
        self.errors = list()
        self.db = self.default_settings
        self.schema = {}
        self.load()
        self.load_schema()

    @property
    def default_settings(self):
        default_settings = dict(ACCEPT_CN_LICENSE="",
                                CN_VERSION="",
                                TEST_ENVIRONMENT="",
                                CN_UPGRADE_TARGET_VERSION="",
                                CN_HELM_RELEASE_NAME="",
                                NGINX_INGRESS_RELEASE_NAME="",
                                NGINX_INGRESS_NAMESPACE="",
                                INSTALL_GLUU_GATEWAY="",
                                POSTGRES_NAMESPACE="",
                                KONG_NAMESPACE="",
                                GLUU_GATEWAY_UI_NAMESPACE="",
                                KONG_PG_USER="",
                                KONG_PG_PASSWORD="",
                                GLUU_GATEWAY_UI_PG_USER="",
                                GLUU_GATEWAY_UI_PG_PASSWORD="",
                                KONG_DATABASE="",
                                GLUU_GATEWAY_UI_DATABASE="",
                                POSTGRES_REPLICAS="",
                                POSTGRES_URL="",
                                KONG_HELM_RELEASE_NAME="",
                                GLUU_GATEWAY_UI_HELM_RELEASE_NAME="",
                                USE_ISTIO="",
                                USE_ISTIO_INGRESS="",
                                ISTIO_SYSTEM_NAMESPACE="",
                                NODES_IPS=[],
                                NODES_ZONES=[],
                                NODES_NAMES=[],
                                NODE_SSH_KEY="",
                                HOST_EXT_IP="",
                                VERIFY_EXT_IP="",
                                AWS_LB_TYPE="",
                                USE_ARN="",
                                VPC_CIDR="",
                                ARN_AWS_IAM="",
                                LB_ADD="",
                                REDIS_URL="",
                                REDIS_TYPE="",
                                REDIS_PW="",
                                REDIS_USE_SSL="false",
                                REDIS_SSL_TRUSTSTORE="",
                                REDIS_SENTINEL_GROUP="",
                                REDIS_MASTER_NODES="",
                                REDIS_NODES_PER_MASTER="",
                                REDIS_NAMESPACE="",
                                INSTALL_REDIS="",
                                INSTALL_JACKRABBIT="",
                                JACKRABBIT_STORAGE_SIZE="",
                                JACKRABBIT_URL="",
                                JACKRABBIT_ADMIN_ID="",
                                JACKRABBIT_ADMIN_PASSWORD="",
                                JACKRABBIT_CLUSTER="",
                                JACKRABBIT_PG_USER="",
                                JACKRABBIT_PG_PASSWORD="",
                                JACKRABBIT_DATABASE="",
                                DEPLOYMENT_ARCH="",
                                PERSISTENCE_BACKEND="",
                                INSTALL_COUCHBASE="",
                                COUCHBASE_NAMESPACE="",
                                COUCHBASE_VOLUME_TYPE="",
                                COUCHBASE_CLUSTER_NAME="",
                                COUCHBASE_URL="",
                                COUCHBASE_USER="",
                                COUCHBASE_SUPERUSER="",
                                COUCHBASE_PASSWORD="",
                                COUCHBASE_SUPERUSER_PASSWORD="",
                                COUCHBASE_CRT="",
                                COUCHBASE_CN="",
                                COUCHBASE_INDEX_NUM_REPLICA="",
                                COUCHBASE_SUBJECT_ALT_NAME="",
                                COUCHBASE_CLUSTER_FILE_OVERRIDE="",
                                COUCHBASE_USE_LOW_RESOURCES="",
                                COUCHBASE_DATA_NODES="",
                                COUCHBASE_QUERY_NODES="",
                                COUCHBASE_INDEX_NODES="",
                                COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES="",
                                COUCHBASE_GENERAL_STORAGE="",
                                COUCHBASE_DATA_STORAGE="",
                                COUCHBASE_INDEX_STORAGE="",
                                COUCHBASE_QUERY_STORAGE="",
                                COUCHBASE_ANALYTICS_STORAGE="",
                                COUCHBASE_INCR_BACKUP_SCHEDULE="",
                                COUCHBASE_FULL_BACKUP_SCHEDULE="",
                                COUCHBASE_BACKUP_RETENTION_TIME="",
                                COUCHBASE_BACKUP_STORAGE_SIZE="",
                                LDAP_BACKUP_SCHEDULE="",
                                NUMBER_OF_EXPECTED_USERS="",
                                EXPECTED_TRANSACTIONS_PER_SEC="",
                                USING_CODE_FLOW="",
                                USING_SCIM_FLOW="",
                                USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW="",
                                DEPLOY_MULTI_CLUSTER="",
                                HYBRID_LDAP_HELD_DATA="",
                                LDAP_JACKRABBIT_VOLUME="",
                                APP_VOLUME_TYPE="",
                                LDAP_STATIC_VOLUME_ID="",
                                LDAP_STATIC_DISK_URI="",
                                CN_CACHE_TYPE="",
                                CN_NAMESPACE="",
                                CN_FQDN="",
                                COUNTRY_CODE="",
                                STATE="",
                                EMAIL="",
                                CITY="",
                                ORG_NAME="",
                                GMAIL_ACCOUNT="",
                                GOOGLE_NODE_HOME_DIR="",
                                IS_CN_FQDN_REGISTERED="",
                                LDAP_PW="",
                                ADMIN_PW="",
                                CLIENT_API_APPLICATION_KEYSTORE_CN="",
                                CLIENT_API_ADMIN_KEYSTORE_CN="",
                                LDAP_STORAGE_SIZE="",
                                AUTH_SERVER_REPLICAS="",
                                OXTRUST_REPLICAS="",
                                LDAP_REPLICAS="",
                                OXSHIBBOLETH_REPLICAS="",
                                OXPASSPORT_REPLICAS="",
                                CLIENT_API_REPLICAS="",
                                CASA_REPLICAS="",
                                RADIUS_REPLICAS="",
                                FIDO2_REPLICAS="",
                                SCIM_REPLICAS="",
                                ENABLE_CONFIG_API="",
                                ENABLE_OXTRUST_API="",
                                ENABLE_OXTRUST_TEST_MODE="",
                                ENABLE_CACHE_REFRESH="",
                                ENABLE_CLIENT_API="",
                                ENABLE_FIDO2="",
                                ENABLE_SCIM="",
                                ENABLE_RADIUS="",
                                ENABLE_OXPASSPORT="",
                                ENABLE_OXSHIBBOLETH="",
                                ENABLE_CASA="",
                                ENABLE_AUTH_SERVER_KEY_ROTATE="",
                                ENABLE_OXTRUST_API_BOOLEAN="false",
                                ENABLE_OXTRUST_TEST_MODE_BOOLEAN="false",
                                ENABLE_RADIUS_BOOLEAN="false",
                                ENABLE_OXPASSPORT_BOOLEAN="false",
                                ENABLE_CASA_BOOLEAN="false",
                                ENABLE_SAML_BOOLEAN="false",
                                ENABLED_SERVICES_LIST=["config", "auth-server", "oxtrust", "persistence", "jackrabbit"],
                                AUTH_SERVER_KEYS_LIFE="",
                                EDIT_IMAGE_NAMES_TAGS="",
                                CASA_IMAGE_NAME="",
                                CASA_IMAGE_TAG="",
                                CONFIG_IMAGE_NAME="",
                                CONFIG_IMAGE_TAG="",
                                CACHE_REFRESH_ROTATE_IMAGE_NAME="",
                                CACHE_REFRESH_ROTATE_IMAGE_TAG="",
                                CERT_MANAGER_IMAGE_NAME="",
                                CERT_MANAGER_IMAGE_TAG="",
                                LDAP_IMAGE_NAME="",
                                LDAP_IMAGE_TAG="",
                                JACKRABBIT_IMAGE_NAME="",
                                JACKRABBIT_IMAGE_TAG="",
                                AUTH_SERVER_IMAGE_NAME="",
                                AUTH_SERVER_IMAGE_TAG="",
                                FIDO2_IMAGE_NAME="",
                                FIDO2_IMAGE_TAG="",
                                SCIM_IMAGE_NAME="",
                                SCIM_IMAGE_TAG="",
                                CLIENT_API_IMAGE_NAME="",
                                CLIENT_API_IMAGE_TAG="",
                                OXPASSPORT_IMAGE_NAME="",
                                OXPASSPORT_IMAGE_TAG="",
                                OXSHIBBOLETH_IMAGE_NAME="",
                                OXSHIBBOLETH_IMAGE_TAG="",
                                OXTRUST_IMAGE_NAME="",
                                OXTRUST_IMAGE_TAG="",
                                PERSISTENCE_IMAGE_NAME="",
                                PERSISTENCE_IMAGE_TAG="",
                                RADIUS_IMAGE_NAME="",
                                RADIUS_IMAGE_TAG="",
                                GLUU_GATEWAY_IMAGE_NAME="",
                                GLUU_GATEWAY_IMAGE_TAG="",
                                GLUU_GATEWAY_UI_IMAGE_NAME="",
                                GLUU_GATEWAY_UI_IMAGE_TAG="",
                                UPGRADE_IMAGE_NAME="",
                                UPGRADE_IMAGE_TAG="",
                                CONFIRM_PARAMS="N"
                                )
        return default_settings

    def load(self):
        """
        Get merged settings (default and custom settings from json file).
        """
        # Check if running in container and settings.json mounted
        try:
            shutil.copy(Path("./installer-settings.json"), "./settings.json")
        except FileNotFoundError:
            # No installation settings mounted as /installer-settings.json. Checking settings.json.
            pass

        try:
            with open(self.setting_file) as f:
                try:
                    custom_settings = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    self.errors.append(f"Non valid settings.json: {str(e)}")
                    return
            self.db.update(custom_settings)
        except FileNotFoundError:
            pass

    def load_schema(self):
        try:
            with open(self.setting_schema) as f:
                try:
                    self.schema = json.load(f)
                    jsonschema.Draft7Validator.check_schema(self.schema)
                except json.decoder.JSONDecodeError as e:
                    logger.info(
                        f"Opps! settings_schema.json not readable")
                    sys.exit(4)
                except jsonschema.SchemaError as e:
                    logger.info(
                        f"Opps! settings_schema.json is invalid")
                    sys.exit(4)
        except FileNotFoundError:
            logger.info(f"Opps! settings_schema.json not found")
            sys.exit(4)

    def store_data(self):
        try:
            update_settings_json_file(self.db)
            return True
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def set(self, key, value):
        """
        single update
        """
        try:
            # TODO: Enabled services should not contain duplicate values from the start.
            if key == "ENABLED_SERVICES_LIST":
                value = list(set(value))
            self.db[str(key)] = value
            self.store_data()
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def get(self, key):
        try:
            return self.db[key]
        except KeyError:
            logger.info("No Value Can Be Found for " + str(key))
            return False

    def get_all(self):
        return self.db

    def update(self, collection):
        """
        mass update
        """
        try:
            self.db.update(collection)
            self.store_data()
            return True
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def reset_data(self):
        """
        reset settings.json to default_settings
        """
        try:
            self.db = self.default_settings
            self.store_data()
            return True
        except Exception as exc:
            logger.info(f"Uncaught error={exc}")
            return False

    def is_exist(self):
        try:
            self.setting_file.resolve(strict=True)
        except FileNotFoundError:
            return False
        else:
            return True

    def validate(self):
        self.errors = []
        try:
            with open(self.setting_file) as f:
                try:
                    settings = json.load(f)
                    validator = jsonschema.Draft7Validator(self.schema)
                    errors = sorted(validator.iter_errors(settings),
                                    key=lambda e: e.path)

                    for error in errors:
                        if "errors" in error.schema and \
                                error.validator != 'required':
                            key = error.path[0]
                            error_msg = error.schema.get('errors').get(
                                error.validator)
                            message = f"{key} : {error_msg}"
                        else:
                            if error.path:
                                key = error.path[0]
                                message = f"{key} : {error.message}"
                            else:
                                message = error.message

                        self.errors.append(message)

                except json.decoder.JSONDecodeError as e:
                    self.errors.append(f"Not a valid settings.json : {str(e)}")
                    return False

        except FileNotFoundError:
            #skip validating file does not exist
            return True

        return len(self.errors) == 0
