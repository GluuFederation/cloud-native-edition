"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
"""
import subprocess
import shlex
import logging
import json
import errno
import socket
import shutil
import os
import string
import random
import re
from getpass import getpass
from pathlib import Path
from .kubeapi import Kubernetes
from ast import literal_eval


def update_settings_json_file(settings):
    """Write settings out to a json file
    :param settings:
    """
    with open(Path('./settings.json'), 'w+') as file:
        json.dump(settings, file, indent=2)


def exec_cmd(cmd):
    """
    Execute command cmd
    :param cmd:
    :return:
    """
    args = shlex.split(cmd)
    popen = subprocess.Popen(args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    retcode = popen.returncode

    if retcode != 0:
        logger.error(str(stderr, "utf-8"))
    logger.info(str(stdout, "utf-8"))
    return stdout, stderr, retcode


def get_logger(name):
    """
    Set logger configs with name.
    :param name:
    :return:
    """
    log_format = '%(asctime)s - %(name)8s - %(levelname)5s - %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        filename='setup.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)


def subprocess_cmd(command):
    """Execute command
    :param command:
    :return:
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def ssh_and_remove(key, user, node_ip, folder_to_be_removed):
    """Execute ssh command and remove directory.
    :param key:
    :param user:
    :param node_ip:
    :param folder_to_be_removed:
    """
    subprocess_cmd("ssh -oStrictHostKeyChecking=no -i {} {}@{} sudo rm -rf {}"
                   .format(key, user, node_ip, folder_to_be_removed))


def check_port(host, port):
    """Check if ports are open
    :param host:
    :param port:
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        conn = sock.connect_ex((host, port))
        if conn == 0:
            # port is not available
            return False
        return True


def copy(src, dest):
    """
    Copy from source to destination
    :param src:
    :param dest:
    """
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            logger.error('Directory not copied. Error: {}'.format(e))


def copy_templates():
    """
    Copy templates folder. /pygluu/kubernetes/templates to working dir.
    """
    entries = Path(
        os.path.join(os.path.dirname(__file__), "templates")
    )
    curdir = os.getcwd()
    for entry in entries.iterdir():
        dst = os.path.join(curdir, entry.name)
        if os.path.exists(dst):
            continue
        copy(entry, dst)


def check_microk8s_kube_config_file():
    """
    Copy microk8s kuber config to ~/.kube/config
    """
    kube_config_file_location = Path(os.path.expanduser("~/.kube/config"))

    if not kube_config_file_location.exists():
        kube_dir = os.path.dirname(kube_config_file_location)

        if not os.path.exists(kube_dir):
            os.makedirs(kube_dir)

        try:
            shutil.copy(Path("/var/snap/microk8s/current/credentials/client.config"), kube_config_file_location)
        except FileNotFoundError:
            logger.error("No Kubernetes config file found at ~/.kube/config")


def prompt_password(password):
    """
    Returns randomally generated password,
    :param password: string for the prompt name
    :return:
    """
    chars = string.ascii_letters + string.digits + string.punctuation + string.punctuation
    keystore_chars = string.ascii_letters + string.digits
    chars = chars.replace('"', '')
    chars = chars.replace("'", "")
    chars = chars.replace("$", "")
    chars = chars.replace("/", "")
    chars = chars.replace("!", "")
    while True:
        while True:
            random_password = ''.join(random.choice(chars) for _ in range(6))
            regex_bool = re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z0-9\S]{6,}$', random_password)
            if regex_bool:
                break
        if password == "OXD-server":
            random_password = ''.join(random.choice(keystore_chars) for _ in range(12))

        if password == "Redis":
            random_password = ''

        string_random_password = random_password[:1] + "***" + random_password[4:]
        pw_prompt = getpass(prompt='{} password [{}]: '.format(password, string_random_password), stream=None)
        if not pw_prompt:
            pw_prompt = random_password
            confirm_pw_prompt = random_password
        else:
            confirm_pw_prompt = getpass(prompt='Confirm password: ', stream=None)
            regex_bool = True
            if password != "OXD-server" and password != "Redis":
                regex_bool = re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z0-9\S]{6,}$', pw_prompt)

        if confirm_pw_prompt != pw_prompt:
            logger.error("Passwords do not match")
        elif not regex_bool:
            logger.error("Password does not meet requirements. The password must container one digit, one uppercase"
                         " letter, one lower case letter and one symbol")
        else:
            logger.info("Success! {} password was set.".format(password))
            return pw_prompt


def register_op_client(namespace, client_name, op_host, oxd_url):
    """
    Registers an op client using oxd.
    :param namespace:
    :param client_name:
    :param op_host:
    :param oxd_url:
    :return:
    """
    kubernetes = Kubernetes()
    logger.info("Registering a client : {}".format(client_name))

    add_curl = ["apk", "add", "curl"]
    data = '{"redirect_uris": ["https://' + op_host + '/gg-ui/"], "op_host": "' + op_host + \
           '", "post_logout_redirect_uris": ["https://' + op_host + \
           '/gg-ui/"], "scope": ["openid", "oxd", "permission", "username"], ' \
           '"grant_types": ["authorization_code", "client_credentials"], "client_name": "' + client_name + '"}'

    exec_curl_command = ["curl", "-k", "-s", "--location", "--request", "POST",
                         "{}/register-site".format(oxd_url), "--header",
                         "Content-Type: application/json", "--data-raw",
                         data]

    kubernetes.connect_get_namespaced_pod_exec(exec_command=add_curl,
                                               app_label="app=oxtrust",
                                               namespace=namespace)
    client_registration_response = \
        kubernetes.connect_get_namespaced_pod_exec(exec_command=exec_curl_command,
                                                   app_label="app=oxtrust",
                                                   namespace=namespace)

    client_registration_response_dict = literal_eval(client_registration_response)
    oxd_id = client_registration_response_dict["oxd_id"]
    client_id = client_registration_response_dict["client_id"]
    client_secret = client_registration_response_dict["client_secret"]
    return oxd_id, client_id, client_secret


logger = get_logger("gluu-common        ")
