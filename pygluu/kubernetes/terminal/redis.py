"""
pygluu.kubernetes.terminal.redis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for terminal redis prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click

from pygluu.kubernetes.helpers import get_logger, prompt_password
from pygluu.kubernetes.terminal.helpers import confirm_yesno

logger = get_logger("gluu-prompt-redis  ")


class PromptRedis:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_redis(self):
        """Prompts for Redis
        """
        if not self.settings.get("REDIS_TYPE"):
            logger.info("STANDALONE, CLUSTER")
            self.settings.set("REDIS_TYPE", click.prompt("Please enter redis type", default="CLUSTER"))

        if not self.settings.get("INSTALL_REDIS"):
            logger.info("For the following prompt if placed [N] the Redis is assumed to be"
                        " installed or remotely provisioned")
            self.settings.set("INSTALL_REDIS", confirm_yesno("Install Redis", default=True))

        if self.settings.get("INSTALL_REDIS") == "Y":
            if not self.settings.get("REDIS_NAMESPACE"):
                self.settings.set("REDIS_NAMESPACE", click.prompt("Please enter a namespace for Redis cluster",
                                                                  default="gluu-redis-cluster"))
        else:
            if not self.settings.get("REDIS_PW"):
                self.settings.set("REDIS_PW", prompt_password("Redis"))

        if not self.settings.get("REDIS_URL"):
            if self.settings.get("INSTALL_REDIS") == "Y":
                redis_url_prompt = "redis-cluster.{}.svc.cluster.local:6379".format(
                    self.settings.get("REDIS_NAMESPACE"))
            else:
                logger.info(
                    "Redis URL can be : redis-cluster.gluu-redis-cluster.svc.cluster.local:6379 in a redis deployment")
                logger.info("Redis URL using AWS ElastiCach [Configuration Endpoint]: "
                            "clustercfg.testing-redis.icrbdv.euc1.cache.amazonaws.com:6379")
                logger.info("Redis URL using Google MemoryStore : <ip>:6379")
                redis_url_prompt = click.prompt(
                    "Please enter redis URL. If you are deploying redis",
                    default="redis-cluster.gluu-redis-cluster.svc.cluster.local:6379",
                )
            self.settings.set("REDIS_URL", redis_url_prompt)
