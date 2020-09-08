"""
pygluu.kubernetes.terminal.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for postgres terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

import click


class PromptPostgres:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_postgres(self):
        """Prompts for PostGres. Injected in a file postgres.yaml used with kubedb
        """
        if not self.settings.get("POSTGRES_NAMESPACE"):
            namespace = click.prompt("Please enter a namespace for postgres", default="postgres")
            self.settings.set("POSTGRES_NAMESPACE", namespace)

        if not self.settings.get("POSTGRES_REPLICAS"):
            replicas = click.prompt("Please enter number of replicas for postgres", default=3)
            self.settings.set("POSTGRES_REPLICAS", replicas)

        if not self.settings.get("POSTGRES_URL"):
            url = click.prompt(
                "Please enter  postgres (remote or local) "
                "URL base name. If postgres is to be installed",
                default=f"postgres.{self.settings.get('POSTGRES_NAMESPACE')}.svc.cluster.local",
            )
            self.settings.set("POSTGRES_URL", url)
