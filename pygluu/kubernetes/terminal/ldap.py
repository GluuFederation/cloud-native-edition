"""
pygluu.kubernetes.terminal.ldap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for ldap terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptLdap:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.enabled_services = self.settings.get("ENABLED_SERVICES_LIST")

    def prompt_hybrid_ldap_held_data(self):
        """Prompts for data held in ldap when hybrid mode is chosen in persistence
        """
        hybrid_ldap_map = {
            1: "default",
            2: "user",
            3: "site",
            4: "cache",
            5: "token",
        }

        if self.settings.get("HYBRID_LDAP_HELD_DATA") not in hybrid_ldap_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Hybrid [WrendDS + Couchbase]                 |")
            print("|------------------------------------------------------------------|")
            print("| [1] Default                                                      |")
            print("| [2] User                                                         |")
            print("| [3] Site                                                         |")
            print("| [4] Cache                                                        |")
            print("| [5] Token                                                        |")
            print("|------------------------------------------------------------------|")

            choice = click.prompt("Cache layer", default=1)
            self.settings.set("HYBRID_LDAP_HELD_DATA", hybrid_ldap_map.get(choice, "default"))
