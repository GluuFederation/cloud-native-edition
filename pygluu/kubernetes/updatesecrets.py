"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 This script helps with editing GLuu secrets without manually tampering with the secrets.
"""
# TODO: Delete this script as soon as the update secret is moved to backend


from pathlib import Path
import base64
from pyDes import *
from .yamlparser import Parser
from .common import get_logger

logger = get_logger("secret-yaml-parser   ")

pydes_secrets = [
           "api_rp_jks_base64",
           "api_rs_jks_base64",
           "ldap_pkcs12_base64",
           "ldap_ssl_cacert",
           "ldap_ssl_cert",
           "ldap_ssl_key",
           "oxauth_jks_base64",
           "passport_rp_client_cert_base64",
           "passport_rp_jks_base64",
           "passport_rs_jks_base64",
           "passport_sp_cert_base64",
           "passport_sp_key_base64",
           "radius_jks_base64",
           "scim_rp_jks_base64",
           "scim_rs_jks_base64",
           "shibIDP_cert",
           "shibIDP_jks_base64",
           "shibIDP_key"
]

base64_secrets = [
           "gluu_ro_client_base64_jwks",
           "idp3EncryptionCertificateText",
           "idp3EncryptionKeyText",
           "idp3SigningCertificateText",
           "idp3SigningKeyText",
           "oxauth_openid_key_base64",
           "passport_rp_client_base64_jwks",
           "passport_rs_client_base64_jwks",
           "scim_rp_client_base64_jwks",
           "scim_rs_client_base64_jwks",
           "ssl_cert",
           "ssl_key"
]


def encode_base64(string):
    """
    Returns encoded string
    :param string:
    :return:
    """
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_str = str(encoded_bytes, "utf-8")
    return encoded_str


def decode_base64(string):
    """
    Returns Base64 decoded string
    :param string:
    :return:
    """
    return base64.b64decode(string).decode('utf-8')


def encode_pydes(data="", salt_key=""):
    """
    Returns encoded PyDes data using salt key
    :param data:
    :param salt_key:
    :return:
    """
    engine = triple_des(salt_key, ECB, pad=None, padmode=PAD_PKCS5)
    data = data.encode('ascii')
    en_data = engine.encrypt(data)
    return base64.b64encode(en_data).decode('utf-8')


def modify_tls(key, value):
    """
    Reads Gluus https TLS certificate and key and updated it with the corresponding value
    :param key:
    :param value:
    """
    tls_yaml_parser = Parser("gluu_tls_certificate.yaml", "Secret")
    if key == "crt":
        logger.info("Editing cert tls secret ")
        tls_yaml_parser["data"]["tls.crt"] = value
    elif key == "key":
        logger.info("Editing key tls secret ")
        tls_yaml_parser["data"]["tls.key"] = value
    tls_yaml_parser.dump_it()


def modify_secret():
    """
    Modify Gluu Secrets
    """
    input("Please place your gluu secret as gluu_secret.yaml. Press Enter when ready")
    secret_yaml_parser = Parser("gluu_secret.yaml", "Secret")
    encoded_salt_key = secret_yaml_parser["data"]["encoded_salt"]
    salt_key = decode_base64(encoded_salt_key)

    for secret_key in pydes_secrets:
        file_of_secret = Path("./" + secret_key)
        if file_of_secret.exists():
            logger.info("Editing secret {}".format(secret_key))
            secret_value = open(file_of_secret).read()
            pydes_secret_key = encode_pydes(secret_value, salt_key)
            secret_yaml_parser["data"][secret_key] = pydes_secret_key

    for secret_key in base64_secrets:
        file_of_secret = Path("./" + secret_key)
        if file_of_secret.exists():
            logger.info("Editing secret {}".format(secret_key))
            secret_value = open(file_of_secret).read()
            base64_secret_key = encode_base64(secret_value)
            secret_yaml_parser["data"][secret_key] = base64_secret_key
            if secret_key == "ssl_cert":
                modify_tls("crt", base64_secret_key)
            elif secret_key == "ssl_key":
                modify_tls("key", base64_secret_key)

    secret_yaml_parser.dump_it()


