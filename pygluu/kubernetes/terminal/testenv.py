"""
pygluu.kubernetes.terminal.testenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for terminal test environment prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click
from pygluu.kubernetes.terminal.helpers import confirm_yesno
from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-prompt-test-env")


class PromptTestEnvironment:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_test_environment(self):
        """Prompts for test environment.
        """
        logger.info("A test environment means that the installer will strip all resource requirements, "
                    "and hence will use as much as needed only. The pods are subject to eviction. Please use "
                    " at least 8GB Ram , 4 CPU, and 50 GB disk.")
        self.settings.set("TEST_ENVIRONMENT", confirm_yesno("Is this a test environment."))

    def prompt_ssh_key(self):
        """Prompts for ssh key if local volumes are used ( Normally used in test envs).
        """
        self.settings.set("NODE_SSH_KEY", click.prompt(
            "Please enter the ssh key path if exists to login into the nodes created. This ssh key will only"
            " be used to delete folders created on the nodes by the setup if the user uses local volumes",
            default="~/.ssh/id_rsa",
        ))
