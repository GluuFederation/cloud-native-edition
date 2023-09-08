"""
pygluu.kubernetes.terminal.doc_store
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for document store terminal prompt.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptDocStore:
    def __init__(self, settings):
        self.settings = settings

    def prompt_doc_store(self):
        """Prompt for document store input."""
        if not self.settings.get("DOCUMENT_STORE_TYPE"):
            self.settings.set(
                "DOCUMENT_STORE_TYPE",
                click.prompt("Document store type", type=click.Choice(["DB", "JCA"]))
            )
