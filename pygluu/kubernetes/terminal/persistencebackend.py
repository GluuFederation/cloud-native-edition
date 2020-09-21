"""
pygluu.kubernetes.terminal.persistencebackend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for persistence backend terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptPersistenceBackend:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.enabled_services = self.settings.get("ENABLED_SERVICES_LIST")

    def prompt_persistence_backend(self):
        """Prompts for persistence backend layer
        """
        persistence_map = {
            1: "ldap",
            2: "couchbase",
            3: "hybrid",
        }

        if self.settings.get("PERSISTENCE_BACKEND") not in persistence_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Persistence layer                            |")
            print("|------------------------------------------------------------------|")
            print("| [1] WrenDS [default]                                             |")
            print("| [2] Couchbase                                                    |")
            print("| [3] Hybrid(WrenDS + Couchbase)                                   |")
            print("|------------------------------------------------------------------|")

            choice = click.prompt("Persistence layer", default=1)
            self.settings.set("PERSISTENCE_BACKEND", persistence_map.get(choice, "ldap"))

        if self.settings.get("PERSISTENCE_BACKEND") == "ldap":
            self.enabled_services.append("ldap")
            self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)
