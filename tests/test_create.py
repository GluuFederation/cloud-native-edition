from pygluu.kubernetes.gluu import Gluu
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.terminal.prompt import Prompt
from pygluu.kubernetes.settings import ValuesHandler
from pytest_console_scripts import ScriptRunner
from pygluu.kubernetes.terminal.helm import PromptHelm
from pygluu.kubernetes.terminal.upgrade import PromptUpgrade
from pygluu.kubernetes.terminal.couchbase import PromptCouchbase

settings = ValuesHandler()

import sys
import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(title="Commands", dest="subparser_name")

prompt_couchbase = PromptCouchbase(settings)
prompt_couchbase.prompt_couchbase()

def test_version(script_runner):
    from pygluu.kubernetes import __version__
    ret = script_runner.run('pygluu-kubernetes', 'version')
    assert args.subparser_name == "version"
    assert ret.stdout == "pygluu installer version is : {__version__}"

def test_install_ldap_backup(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'install-ldap-backup')
    assert args.subparser_name == "install-ldap-backup"
    gluu = Gluu()
    assert gluu.install_ldap_backup()

def test_unset_ldap(caplog, create):
    create.db = str

    with caplog.at_level(logging.INFO):
        assert args.subparser_name == "install-ldap-backup"
        settings.set("installer-settings.redis.install", True) 
        assert "remove me after implementing TODO" in caplog.text

def test_uninstall_gluu(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'uninstall-gluu')
    prompt_helm = PromptHelm(settings)
    prompt_helm.prompt_helm()
    gluu = Gluu()
    gluu.install_ldap_backup()
    assert ret.success
    assert ret.stderr == ""

def test_upgrade(script_runner, caplog):
    ret = script_runner.run('pygluu-kubernetes', 'upgrade-values-yaml')
    gluu = Gluu()
    settings.set("installer-settings.jackrabbit.clusterMode", True)
    settings.set("installer-settings.postgres.install", True)
    assert "remove me after implementing TODO" in caplog.text
    assert ret.success

def test_couchbase(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'install-couchbase')
    prompt_couchbase = PromptCouchbase(settings)
    prompt_couchbase.prompt_couchbase()
    couchbase = Couchbase()
    couchbase.install()
    assert ret.success
    assert ret.stderr == ""

def test_couchbase_backup(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'install-couchbase-backup')
    prompt_couchbase = PromptCouchbase(settings)
    prompt_couchbase.prompt_couchbase()
    couchbase = Couchbase()
    couchbase.setup_backup_couchbase()
    assert ret.success
    assert ret.stderr == ""

def test_uninstall_couchbase(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'uninstall-couchbase')
    prompt_couchbase = PromptCouchbase(settings)
    prompt_couchbase = PromptCouchbase(settings)
    prompt_couchbase.prompt_couchbase()
    couchbase = Couchbase()
    couchbase.uninstall()
    assert ret.success
    assert ret.stderr == ""

def test_generate_settings(script_runner, caplog):
    ret = script_runner.run('pygluu-kubernetes', 'generate-settings')
    assert ret.success
    assert ret.stdout == "settings.json has been generated"
    assert "settings.json has been generated" in caplog.text
    assert ret.stderr == ""

def test_install(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'install')
    assert ret.success
    assert ret.stdout == "pygluu installer version is "
    assert ret.stderr == ""

def test_uninstall(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'uninstall')
    assert ret.success
    assert ret.stdout == "pygluu installer version is "
    assert ret.stderr == ""

def test_install_gluu(script_runner):
    ret = script_runner.run('pygluu-kubernetes', 'install-gluu')
    assert ret.success
    assert ret.stdout == "pygluu installer version is "
    assert ret.stderr == ""