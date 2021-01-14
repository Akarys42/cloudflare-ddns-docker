import logging
import threading
from dataclasses import dataclass
from typing import Tuple, List, Dict, NoReturn

import requests

from cloudflare_ddns.constants import VERIFY_TOKEN, LIST_ZONES, LIST_DNS, ACCEPTED_RECORDS
from cloudflare_ddns.utils import parse_duration, BearerAuth

log = logging.getLogger("ddns")


@dataclass
class Domain:
    domain: str
    record_type: str
    zone: str
    id: str


class ApplicationJob(threading.Thread):
    def __init__(self, raw_delay: str, token: str, raw_domains: Tuple[str], default_ipv6: bool):
        super().__init__()

        self.stop_signal = threading.Event()

        self.delay = None
        self.domains: List[Domain] = []
        self.found_domains: Dict[str, Domain] = {}

        self.auth = BearerAuth(token)
        self.default_ipv6 = default_ipv6

        self.raw_domains = raw_domains
        self.raw_delay = raw_delay

    def launch(self) -> None:
        self.validate_arguments()
        log.debug("Starting job.")
        self.start()

    def run(self) -> None:
        log.debug("Parsing domains.")
        self.parse_domains()
        log.debug(f"Using domains: {', '.join(f'{domain.record_type}:{domain.domain}' for domain in self.domains)}")

        log.info("Starting app.")
        self.update_records()
        while not self.stop_signal.wait(self.delay):
            self.update_records()

    def update_records(self):
        ...

    def parse_domains(self):
        type_1 = "A" if not self.default_ipv6 else "AAAA"
        type_2 = "A" if self.default_ipv6 else "AAAA"

        for zone_json in requests.get(LIST_ZONES, auth=self.auth).json()["result"]:
            for record_json in requests.get(
                    LIST_DNS.format(zone_identifier=zone_json["id"]),
                    auth=self.auth
            ).json()["result"]:
                if record_json["type"] in ACCEPTED_RECORDS:
                    domain = Domain(
                        record_json["name"],
                        record_json["type"],
                        record_json["zone_id"],
                        record_json["id"]
                    )
                    self.found_domains[f'{record_json["name"]}-{record_json["type"]}'] = domain

        log.debug(
            f"Found domains: "
            f"{', '.join(f'{domain.record_type}:{domain.domain}' for domain in self.found_domains.values())}"
        )
        for domain in self.raw_domains:
            if ':' in domain:
                type_, domain = domain.split(':', maxsplit=1)

                if type_ not in ACCEPTED_RECORDS:
                    log.error(f"Invalid record type {type_}. Must be one of {', '.join(ACCEPTED_RECORDS)}.")
                    log.info(f"Exiting with code 65.")
                    exit(65)

                if f"{domain}-{type_}" not in self.found_domains:
                    log.error(
                        f"Cannot find an {type_} record for the domain {domain} in your Cloudflare settings. "
                        f"Have you defined this record yet?"
                    )
                    log.info(f"Exiting with code 65.")
                    exit(65)
            else:
                if f"{domain}-{type_1}" in self.found_domains:
                    type_ = type_1
                elif f"{domain}-{type_2}" in self.found_domains:
                    type_ = type_2
                else:
                    log.error(
                        f"Cannot find the domain {domain} in your Cloudflare settings. "
                        f"Have you defined this record yet?"
                    )
                    log.info(f"Exiting with code 65.")
                    exit(65)

            self.domains.append(self.found_domains[f"{domain}-{type_}"])




    def validate_arguments(self):
        failed = False

        if not self.raw_domains:
            log.error("Please provide at least one domain.")
            failed = True

        try:
            self.delay = parse_duration(self.raw_delay)
        except ValueError as e:
            log.error(f"Failed to parse delay: {e}")
            failed = True

        if not failed:
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
