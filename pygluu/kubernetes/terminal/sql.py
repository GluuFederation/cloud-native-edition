"""
pygluu.kubernetes.terminal.sql
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for jackrabbit terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click

from pygluu.kubernetes.helpers import get_logger, prompt_password
from pygluu.kubernetes.terminal.helpers import confirm_yesno

logger = get_logger("gluu-prompt-sql")


class PromptSQL:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_sql(self):
        """Prompts for SQL server
        """
        sql_dialect = {
            1: "mysql",
            2: "pgsql",
        }

        if self.settings.get("GLUU_SQL_DB_DIALECT") not in sql_dialect.values():
            print("|------------------------------------------------------------------|")
            print("|                     SQL DIALECT                                  |")
            print("|------------------------------------------------------------------|")
            print("| [1] MySQL                                                        |")
            print("| [2] PostgreSQL - UNDERDEV                                        |")
            print("|------------------------------------------------------------------|")

            choice = click.prompt("SQL dialect", default=1)
            self.settings.set("GLUU_SQL_DB_DIALECT", sql_dialect.get(choice, "mysql"))

        if not self.settings.get("GLUU_INSTALL_SQL"):
            logger.info(
                "Install SQL dialect from Bitnamis charts.If the following prompt is answered with N it is assumed "
                "the SQL server is installed remotely or locally by the user."
                " A managed service such as Amazon Aurora or CloudSQL should be used in production setups.")
            self.settings.set("GLUU_INSTALL_SQL",
                              confirm_yesno("Install SQL dialect from Bitnamis charts", default=True))

        if self.settings.get("GLUU_INSTALL_SQL") == "Y":
            self.settings.set("GLUU_SQL_DB_PORT", 3306)
            if not self.settings.get("GLUU_SQL_DB_NAMESPACE"):
                self.settings.set("GLUU_SQL_DB_NAMESPACE",
                                  click.prompt("Please enter a namespace for the SQL server", default="sql"))

            self.settings.set("GLUU_SQL_DB_HOST",
                              f'gluu-mysql.{self.settings.get("GLUU_SQL_DB_NAMESPACE")}.svc.cluster.local')
            if self.settings.get("GLUU_SQL_DB_DIALECT") == "pgsql":
                self.settings.set("INSTALL_POSTGRES", "Y")
                self.settings.set("GLUU_SQL_DB_HOST",
                                  f'gluu-postgresql.{self.settings.get("GLUU_SQL_DB_NAMESPACE")}.svc.cluster.local')
                self.settings.set("GLUU_SQL_DB_PORT", 5432)
        if not self.settings.get("GLUU_SQL_DB_HOST"):
            self.settings.set("GLUU_SQL_DB_HOST", click.prompt("Please enter  SQL (remote or local) URL base name",
                                                               default="gluu.sql.svc.cluster.local"))

        if not self.settings.get("GLUU_SQL_DB_PORT"):
            self.settings.set("GLUU_SQL_DB_PORT", click.prompt("Please enter  SQL (remote or local) port number",
                                                               default=3306))

        if not self.settings.get("GLUU_SQL_DB_USER"):
            self.settings.set("GLUU_SQL_DB_USER", click.prompt("Please enter a user for Gluu SQL database ",
                                                               default="gluu"))

        if not self.settings.get("GLUU_SQL_DB_PASSWORD"):
            self.settings.set("GLUU_SQL_DB_PASSWORD", prompt_password("gluu-db-sql"))

        if not self.settings.get("GLUU_SQL_DB_NAME"):
            self.settings.set("GLUU_SQL_DB_NAME", click.prompt("Please enter Gluu SQL database name",
                                                               default="gluu"))
