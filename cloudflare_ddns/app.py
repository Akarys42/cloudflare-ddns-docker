import logging
import threading
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests
from cloudflare_ddns.constants import ACCEPTED_RECORDS, LIST_DNS, LIST_ZONES, VERIFY_TOKEN, PATCH_DNS
from cloudflare_ddns.utils import BearerAuth, parse_duration, get_ip

log = logging.getLogger("ddns")


@dataclass
class Domain:
    domain: str
    record_type: str
    zone: str
    id: str


class ApplicationJob(threading.Thread):
    def __init__(self, raw_delay: str, token: str, raw_domains: Tuple[str]):
        super().__init__()

        self.stop_signal = threading.Event()

        self.delay = None
        self.domains: List[Domain] = []
        self.current_ip = None

        self.auth = BearerAuth(token)

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

        log.info(f"Starting app. Records will be updated every {self.delay} seconds.")
        try:
            self.update_records()
        except Exception:
            log.exception("Error while updating records for the first time, aborting.")
            log.info("Exiting with code 70.")
            exit(70)

        while not self.stop_signal.wait(self.delay):
            try:
                self.update_records()
            except Exception:
                log.exception(f"Error while updating records. Retrying in {self.delay} seconds.")

    def update_records(self) -> None:
        log.info("Starting record update.")
        for record in self.domains:
            log.debug(f"Updating record for {record.domain}.")
            requests.patch(
                PATCH_DNS.format(zone_identifier=record.zone, identifier=record.id),
                json={"content": get_ip(record.record_type == 'AAAA')},
                auth=self.auth
            ).raise_for_status()
        log.info("Successfully updated records.")

    def parse_domains(self) -> None:
        found_domains = {}

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
                    found_domains[f'{record_json["name"]}-{record_json["type"]}'] = domain

        log.debug(
            f"Found domains: "
            f"{', '.join(f'{domain.record_type}:{domain.domain}' for domain in found_domains.values())}"
        )
        for domain in self.raw_domains:
            if ':' in domain:
                type_, domain = domain.split(':', maxsplit=1)

                if type_ not in ACCEPTED_RECORDS:
                    log.error(f"Invalid record type {type_}. Must be one of {', '.join(ACCEPTED_RECORDS)}.")
                    log.info(f"Exiting with code 65.")
                    exit(65)

                if f"{domain}-{type_}" not in found_domains:
                    log.error(
                        f"Cannot find an {type_} record for the domain {domain} in your Cloudflare settings. "
                        f"Have you defined this record yet?"
                    )
                    log.info(f"Exiting with code 65.")
                    exit(65)

                self.domains.append(found_domains[f"{domain}-{type_}"])

            else:
                found = False

                if f"{domain}-A" in found_domains:
                    self.domains.append(found_domains[f"{domain}-A"])
                    found = True

                if f"{domain}-AAAA" in found_domains:
                    self.domains.append(found_domains[f"{domain}-AAAA"])
                    found = True

                if not found:
                    log.error(
                        f"Cannot find the domain {domain} in your Cloudflare settings. "
                        f"Have you defined this record yet?"
                    )
                    log.info(f"Exiting with code 65.")
                    exit(65)

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