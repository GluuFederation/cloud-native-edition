"""
pygluu.kubernetes.terminal.confirmsettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for  confirming user settings terminal prompt.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""


import click


class PromptConfirmSettings:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def confirm_params(self):
        """Formats output of settings from prompts to the user. Passwords are not displayed.
        """
        hidden_settings = ["NODES_IPS", "NODES_ZONES", "NODES_NAMES",
                           "COUCHBASE_PASSWORD", "LDAP_PW", "ADMIN_PW", "REDIS_PW",
                           "COUCHBASE_SUBJECT_ALT_NAME", "JACKRABBIT_ADMIN_PASSWORD",
                           "JACKRABBIT_PG_PASSWORD", "GOOGLE_SERVICE_ACCOUNT_BASE64", "GLUU_SQL_DB_PASSWORD", "SALT"]

        print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', 'Setting', '|', 'Value', '|'))
        for k, v in self.settings.db.items():
            if k not in hidden_settings:
                if k in  ("ENABLED_SERVICES_LIST", "GLUU_LDAP_MULTI_CLUSTERS_IDS"):
                    v = ", ".join(self.settings.get(k))
                print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', k, '|', v, '|'))

        if click.confirm("Please confirm the above settings"):
            self.settings.set("CONFIRM_PARAMS", "Y")
        else:
            self.settings.reset_data()
            # Prompt for settings again
            from pygluu.kubernetes.terminal.prompt import Prompt
            initialize_prompts = Prompt()
            initialize_prompts.prompt()
