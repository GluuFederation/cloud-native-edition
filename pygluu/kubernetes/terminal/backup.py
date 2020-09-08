"""
pygluu.kubernetes.terminal.backup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for terminal backup prompt.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptBackup:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_backup(self):
        """Prompt for LDAP and or Couchbase backup strategies
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            if not self.settings.get("COUCHBASE_INCR_BACKUP_SCHEDULE"):
                self.settings.set("COUCHBASE_INCR_BACKUP_SCHEDULE", click.prompt(
                    "Please input couchbase backup cron job schedule for incremental backups. "
                    "This will run backup job every 30 mins by default.",
                    default="*/30 * * * *",
                ))

            if not self.settings.get("COUCHBASE_FULL_BACKUP_SCHEDULE"):
                self.settings.set("COUCHBASE_FULL_BACKUP_SCHEDULE", click.prompt(
                    "Please input couchbase backup cron job schedule for full backups. "
                    "This will run backup job on Saturday at 2am",
                    default="0 2 * * 6",
                ))

            if not self.settings.get("COUCHBASE_BACKUP_RETENTION_TIME"):
                self.settings.set("COUCHBASE_BACKUP_RETENTION_TIME", click.prompt(
                    "Please enter the time period in which to retain existing backups. "
                    "Older backups outside this time frame are deleted",
                    default="168h",
                ))

            if not self.settings.get("COUCHBASE_BACKUP_STORAGE_SIZE"):
                self.settings.set("COUCHBASE_BACKUP_STORAGE_SIZE",
                                  click.prompt("Size of couchbase backup volume storage",
                                               default="20Gi"))

        elif self.settings.get("PERSISTENCE_BACKEND") == "ldap":
            if not self.settings.get("LDAP_BACKUP_SCHEDULE"):
                self.settings.set("LDAP_BACKUP_SCHEDULE", click.prompt(
                    "Please input ldap backup cron job schedule. "
                    "This will run backup job every 30 mins by default.",
                    default="*/30 * * * *",
                ))
