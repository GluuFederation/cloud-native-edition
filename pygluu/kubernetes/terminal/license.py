"""
pygluu.kubernetes.terminal.license
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for terminal license prompt .

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from pygluu.kubernetes.terminal.helpers import confirm_yesno
from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-prompt-license")


class PromptLicense:

    def __init__(self, settings, accept_license=False):
        self.settings = settings
        if accept_license:
            self.settings.set("ACCEPT_GLUU_LICENSE", "Y")
        self.prompt_license()

    def prompt_license(self):
        """Prompts user to accept Apache 2.0 license
        """
        if self.settings.get("ACCEPT_GLUU_LICENSE") != "Y":
            with open("./LICENSE") as f:
                print(f.read())

            self.settings.set("ACCEPT_GLUU_LICENSE", confirm_yesno("Do you accept the Gluu license stated above"))
            if self.settings.get("ACCEPT_GLUU_LICENSE") != "Y":
                logger.info("License not accepted.")
                raise SystemExit(1)
