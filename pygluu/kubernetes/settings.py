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
import shutil
import sys
from pathlib import Path
from pygluu.kubernetes.helpers import get_logger, update_settings_json_file

logger = get_logger("gluu-setting        ")


def unlink_settings_json():
    filename = Path("./settings.json")
    with contextlib.suppress(FileNotFoundError):
        os.unlink(filename)


class SettingsHandler(object):
    def __init__(self):
        self.db = self.default_settings
        self.load()

    @property
    def default_settings(self):
        default_settings = dict(ACCEPT_GLUU_LICENSE="",
                                TEST_ENVIRONMENT="",
                                ADMIN_PW="",
                                GLUU_VERSION="",
                                GLUU_UPGRADE_TARGET_VERSION="",
                                GLUU_HELM_RELEASE_NAME="",
                                NGINX_INGRESS_NAMESPACE="",
                                NGINX_INGRESS_RELEASE_NAME="",
                                USE_ISTIO="",
                                USE_ISTIO_INGRESS="",
                                ISTIO_SYSTEM_NAMESPACE="",
                                POSTGRES_NAMESPACE="",
                                POSTGRES_URL="",
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
                                DEPLOYMENT_ARCH="",
                                PERSISTENCE_BACKEND="",
                                REDIS_URL="",
                                REDIS_TYPE="",
                                REDIS_PW="",
                                REDIS_USE_SSL="false",
                                REDIS_SSL_TRUSTSTORE="",
                                REDIS_SENTINEL_GROUP="",
                                REDIS_NAMESPACE="",
                                INSTALL_REDIS="",
                                INSTALL_POSTGRES="",
                                INSTALL_JACKRABBIT="",
                                JACKRABBIT_STORAGE_SIZE="",
                                JACKRABBIT_URL="",
                                JACKRABBIT_ADMIN_ID="",
                                JACKRABBIT_ADMIN_PASSWORD="",
                                JACKRABBIT_CLUSTER="",
                                JACKRABBIT_PG_USER="",
                                JACKRABBIT_PG_PASSWORD="",
                                JACKRABBIT_DATABASE="",
                                INSTALL_COUCHBASE="",
                                COUCHBASE_NAMESPACE="",
                                COUCHBASE_VOLUME_TYPE="",
                                COUCHBASE_CLUSTER_NAME="",
                                COUCHBASE_URL="",
                                COUCHBASE_USER="",
                                COUCHBASE_BUCKET_PREFIX="",
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
                                GLUU_CACHE_TYPE="",
                                GLUU_NAMESPACE="",
                                GLUU_FQDN="",
                                COUNTRY_CODE="",
                                STATE="",
                                EMAIL="",
                                CITY="",
                                ORG_NAME="",
                                LDAP_PW="",
                                GMAIL_ACCOUNT="",
                                GOOGLE_NODE_HOME_DIR="",
                                IS_GLUU_FQDN_REGISTERED="",
                                OXD_APPLICATION_KEYSTORE_CN="",
                                OXD_ADMIN_KEYSTORE_CN="",
                                LDAP_STORAGE_SIZE="",
                                OXAUTH_KEYS_LIFE="",
                                OXAUTH_REPLICAS="",
                                OXTRUST_REPLICAS="",
                                LDAP_REPLICAS="",
                                OXSHIBBOLETH_REPLICAS="",
                                OXPASSPORT_REPLICAS="",
                                OXD_SERVER_REPLICAS="",
                                CASA_REPLICAS="",
                                FIDO2_REPLICAS="",
                                SCIM_REPLICAS="",
                                ENABLE_OXTRUST_API="",
                                ENABLE_OXTRUST_TEST_MODE="",
                                ENABLE_CACHE_REFRESH="",
                                ENABLE_OXD="",
                                ENABLE_FIDO2="",
                                ENABLE_SCIM="",
                                ENABLE_OXPASSPORT="",
                                ENABLE_OXSHIBBOLETH="",
                                ENABLE_CASA="",
                                ENABLE_OXAUTH_KEY_ROTATE="",
                                ENABLE_OXTRUST_API_BOOLEAN="false",
                                ENABLE_OXTRUST_TEST_MODE_BOOLEAN="false",
                                ENABLE_OXPASSPORT_BOOLEAN="false",
                                ENABLE_CASA_BOOLEAN="false",
                                ENABLE_SAML_BOOLEAN="false",
                                ENABLED_SERVICES_LIST=["config", "oxauth", "oxtrust", "persistence", "jackrabbit"],
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
                                OXAUTH_IMAGE_NAME="",
                                OXAUTH_IMAGE_TAG="",
                                FIDO2_IMAGE_NAME="",
                                FIDO2_IMAGE_TAG="",
                                SCIM_IMAGE_NAME="",
                                SCIM_IMAGE_TAG="",
                                OXD_IMAGE_NAME="",
                                OXD_IMAGE_TAG="",
                                OXPASSPORT_IMAGE_NAME="",
                                OXPASSPORT_IMAGE_TAG="",
                                OXSHIBBOLETH_IMAGE_NAME="",
                                OXSHIBBOLETH_IMAGE_TAG="",
                                OXTRUST_IMAGE_NAME="",
                                OXTRUST_IMAGE_TAG="",
                                PERSISTENCE_IMAGE_NAME="",
                                PERSISTENCE_IMAGE_TAG="",
                                UPGRADE_IMAGE_NAME="",
                                UPGRADE_IMAGE_TAG="",
                                CONFIRM_PARAMS="N",
                                GLUU_LDAP_MULTI_CLUSTER="",
                                GLUU_LDAP_ADVERTISE_ADDRESS_SUFFIX="",
                                GLUU_LDAP_SECONDARY_CLUSTER="",
                                GLUU_LDAP_SERF_PEERS="",
                                GLUU_INSTALL_SQL="",
                                GLUU_SQL_DB_DIALECT="",
                                GLUU_SQL_DB_NAMESPACE="",
                                GLUU_SQL_DB_HOST="",
                                GLUU_SQL_DB_PORT="",
                                GLUU_SQL_DB_NAME="",
                                GLUU_SQL_DB_USER="",
                                GLUU_SQL_DB_PASSWORD="",
                                GOOGLE_SERVICE_ACCOUNT_BASE64="",
                                USE_GOOGLE_SECRET_MANAGER="",
                                GOOGLE_SPANNER_INSTANCE_ID="",
                                GOOGLE_SPANNER_DATABASE_ID="",
                                GOOGLE_PROJECT_ID="",
                                MIGRATION_ENABLED="",
                                MIGRATION_DIR="",
                                MIGRATION_DATA_FORMAT="",
                                GLUU_SCIM_PROTECTION_MODE="",
                                GLUU_LDAP_MULTI_CLUSTER_REPLICAS="",
                                GLUU_LDAP_MULTI_CLUSTER_CLUSTER_ID="",
                                GLUU_LDAP_MULTI_CLUSTER_NAMESPACE_INT_ID="",
                                GLUU_LDAP_MULTI_CLUSTERS_IDS=[],
                                NGINX_LEGACY="",
                                SPANNER_EMULATOR_HOST="",
                                CONTAINER_REGISTRY_SECRET_NAME="",
                                USE_CUSTOM_SALT="",
                                SALT="",
                                DOCUMENT_STORE_TYPE="",
                                )
        return default_settings

    def load(self):
        self.get_settings()

    def get_settings(self):
        """Get merged settings (default and custom settings from json file).
        """
        # Check if running in container and settings.json mounted
        try:
            shutil.copy(Path("./installer-settings.json"), "./settings.json")
        except FileNotFoundError:
            # No installation settings mounted as /installer-settings.json. Checking settings.json.
            pass

        filename = Path("./settings.json")
        try:
            with open(filename) as f:
                try:
                    custom_settings = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    logger.error("Non valid settings.json")
                    logger.error(str(e))
                    sys.exit()
            self.db.update(custom_settings)
        except FileNotFoundError:
            pass

    def store_data(self):
        try:
            update_settings_json_file(self.db)
            # json.dump(self.db, open(self.path, "w+"))
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
        filename = Path("./settings.json")
        try:
            filename.resolve(strict=True)
        except FileNotFoundError:
            return False
        else:
            return True
