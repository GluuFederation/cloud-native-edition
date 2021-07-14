"""
pygluu.kubernetes.terminal.image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for image names and tags terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click

from pygluu.kubernetes.terminal.helpers import confirm_yesno


class PromptImages:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_image_name_tag(self):
        """Manual prompts for image names and tags if changed from default or at a different repository.
        """

        def prompt_and_set_setting(service, image_name_key, image_tag_key):
            self.settings.set(image_name_key,
                              click.prompt(f"{service} image name", default=self.settings.get(image_name_key)))
            self.settings.set(image_tag_key,
                              click.prompt(f"{service} image tag", default=self.settings.get(image_tag_key)))

        if not self.settings.get("EDIT_IMAGE_NAMES_TAGS"):
            self.settings.set("EDIT_IMAGE_NAMES_TAGS", confirm_yesno(
                "Would you like to manually edit the image source/name and tag"))

        if self.settings.get("EDIT_IMAGE_NAMES_TAGS") == "Y":
            # CASA
            if self.settings.get("ENABLE_CASA") == "Y":
                prompt_and_set_setting("Casa", "CASA_IMAGE_NAME", "CASA_IMAGE_TAG")
            # CONFIG
            prompt_and_set_setting("Config", "CONFIG_IMAGE_NAME", "CONFIG_IMAGE_TAG")
            # CACHE_REFRESH_ROTATE
            if self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
                prompt_and_set_setting("CR-rotate", "CACHE_REFRESH_ROTATE_IMAGE_NAME", "CACHE_REFRESH_ROTATE_IMAGE_TAG")
            # KEY_ROTATE
            if self.settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "Y":
                prompt_and_set_setting("Key rotate", "CERT_MANAGER_IMAGE_NAME", "CERT_MANAGER_IMAGE_TAG")
            # LDAP
            if self.settings.get("PERSISTENCE_BACKEND") == "hybrid" or \
                    self.settings.get("PERSISTENCE_BACKEND") == "ldap":
                prompt_and_set_setting("OpenDJ", "LDAP_IMAGE_NAME", "LDAP_IMAGE_TAG")
            # Jackrabbit
            prompt_and_set_setting("jackrabbit", "JACKRABBIT_IMAGE_NAME", "JACKRABBIT_IMAGE_TAG")
            # OXAUTH
            prompt_and_set_setting("oxAuth", "OXAUTH_IMAGE_NAME", "OXAUTH_IMAGE_TAG")
            # OXD
            if self.settings.get("ENABLE_OXD") == "Y":
                prompt_and_set_setting("OXD server", "OXD_IMAGE_NAME", "OXD_IMAGE_TAG")
            # OXPASSPORT
            if self.settings.get("ENABLE_OXPASSPORT") == "Y":
                prompt_and_set_setting("oxPassport", "OXPASSPORT_IMAGE_NAME", "OXPASSPORT_IMAGE_TAG")
            # OXSHIBBBOLETH
            if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
                prompt_and_set_setting("oxShibboleth", "OXSHIBBOLETH_IMAGE_NAME", "OXSHIBBOLETH_IMAGE_TAG")
            # OXTRUST
            prompt_and_set_setting("oxTrust", "OXTRUST_IMAGE_NAME", "OXTRUST_IMAGE_TAG")
            # PERSISTENCE
            prompt_and_set_setting("Persistence", "PERSISTENCE_IMAGE_NAME", "PERSISTENCE_IMAGE_TAG")
            self.settings.set("EDIT_IMAGE_NAMES_TAGS", "N")
