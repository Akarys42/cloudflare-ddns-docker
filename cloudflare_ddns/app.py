import logging
import threading
from dataclasses import dataclass
from typing import Tuple

import requests

from cloudflare_ddns.constants import VERIFY_TOKEN
from cloudflare_ddns.utils import parse_duration, BearerAuth

log = logging.getLogger("ddns")


@dataclass
class Domain:
    domain: str
    record_type: str


class ApplicationJob(threading.Thread):
    def __init__(self, delay: str, token: str, raw_domains: Tuple[str], default_ipv6: bool):
        super().__init__()

        self.stop_signal = threading.Event()

        self.delay = delay
        self.auth = BearerAuth(token)
        self.raw_domains = raw_domains
        self.default_ipv6 = default_ipv6

    def launch(self) -> None:
        self.validate_arguments()

    def validate_arguments(self):
        failed = False

        if not self.raw_domains:
            log.error("Please provide at least one domain.")
            failed = True

        try:
            self.delay = parse_duration(self.delay)
        except ValueError as e:
            log.error(f"Failed to parse delay: {e}")
            failed = True

        try:
            log.debug("Validating bearer token.")

            self.validate_bearer()
        except ValueError as e:
            log.error(f"Failed to validate bearer token: {e}")
            failed = True
        else:
            log.info("Successfully validated the bearer token.")

        if failed:
            log.info("Exiting with code 64.")
            exit(64)

    def validate_bearer(self) -> None:
        """Utility method to validate a CF bearer token."""
        r = requests.get(VERIFY_TOKEN, auth=self.auth)

        if not r.json()["success"]:
            error_message = ' / '.join(error["message"] for error in r.json()["errors"])
            raise ValueError(error_message)
