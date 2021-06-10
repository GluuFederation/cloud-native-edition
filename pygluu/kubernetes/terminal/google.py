"""
pygluu.kubernetes.terminal.google
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for spanner terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click
from pathlib import Path
import base64
from pygluu.kubernetes.terminal.helpers import confirm_yesno
import json


class PromptGoogle:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_google(self):
        """Prompts for spanner ids
        """
        if self.settings.get("PERSISTENCE_BACKEND") == "spanner":
            if not self.settings.get("GOOGLE_SPANNER_INSTANCE_ID"):
                self.settings.set("GOOGLE_SPANNER_INSTANCE_ID",
                                  click.prompt("Please enter the google spanner instance ID.",
                                               default=""))

            if not self.settings.get("GOOGLE_SPANNER_DATABASE_ID"):
                self.settings.set("GOOGLE_SPANNER_DATABASE_ID",
                                  click.prompt("Please enter the google spanner database ID",
                                               default=""))
        # Feature not implemented yet
        self.settings.set("USE_GOOGLE_SECRET_MANAGER", "N")
        if not self.settings.get("USE_GOOGLE_SECRET_MANAGER"):
            self.settings.set("USE_GOOGLE_SECRET_MANAGER",
                              confirm_yesno("[BETA] Use Google Secret Manager to hold gluu configuration layer. "
                                            "If answered with No, kubernetes secrets will be used", default=False))

        if self.settings.get("PERSISTENCE_BACKEND") == "spanner" or \
                self.settings.get("USE_GOOGLE_SECRET_MANAGER") == "Y":
            if not self.settings.get("GOOGLE_SERVICE_ACCOUNT_BASE64"):
                try:
                    print("Place the google service account json file under the name google_service_account.json. at "
                          "the same location as the installation script. The service account must have "
                          "roles/secretmanager.admin to use Google secret manager and/or "
                          "roles/spanner.databaseUser to use Spanner")
                    _ = input("Hit 'enter' or 'return' when ready.")
                    with open(Path("./google_service_account.json")) as content_file:
                        sa = content_file.read()
                        encoded_sa_crt_bytes = base64.b64encode(sa.encode("utf-8"))
                        encoded_sa_crt_string = str(encoded_sa_crt_bytes, "utf-8")
                    self.settings.set("GOOGLE_SERVICE_ACCOUNT_BASE64", encoded_sa_crt_string)
                except FileNotFoundError:
                    print("The google service account json was not found.")
                    raise SystemExit(1)

            if not self.settings.get("GOOGLE_PROJECT_ID"):
                try:
                    with open("google_service_account.json", "r") as google_sa:
                        sa = json.load(google_sa)
                        self.settings.set("GOOGLE_PROJECT_ID", sa["project_id"])
                except FileNotFoundError:
                    print("The google service account json was not found."
                          "your settings.json.")
                    if not self.settings.get("GOOGLE_PROJECT_ID"):
                        self.settings.set("GOOGLE_PROJECT_ID",
                                          click.prompt("Please enter the google project ID",
                                                       default=""))
