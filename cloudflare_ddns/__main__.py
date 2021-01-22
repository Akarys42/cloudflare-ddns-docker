import logging
from os import environ
from typing import Tuple

import click
from cloudflare_ddns.app import ApplicationJob
from cloudflare_ddns.constants import BASE_ENV_VAR, DEFAULT_DELAY, DOMAINS_ENV_VAR

log = logging.getLogger("ddns")


@click.command()
@click.option(
    '--delay', '-d',
    default=DEFAULT_DELAY,
    show_default=True,
    show_envvar=True,
    help="Time to wait between each update."
)
@click.option(
    '--token', '-k',
    prompt="Enter your Cloudflare Token",
    hide_input=True,
    show_envvar=True,
    help="Your Cloudflare Bearer token."
)
@click.option('-v', '--verbose', is_flag=True, default=False, help="Show debug logging.")
@click.argument("domains", nargs=-1)
def start(delay: str, token: str, verbose: int, domains: Tuple[str]) -> None:
    """
    Update Cloudflare DNS RECORDS to your current IP every <delay> (default: 5 minutes).

    The domains can be passed either as command line options, or as a space separated CF_DDNS_DOMAINS environment
    variable.
    Each domain can be preceded by the record type, either A or AAAA followed by a colon.

    \b
    The duration supports the following symbols for each unit of time:
        - days: `d`, `D`, `day`, `days`
        - hours: `H`, `h`, `hour`, `hours`
        - minutes: `M`, `m`, `minute`, `minutes`, `min`
        - seconds: `S`, `s`, `second`, `seconds`, `sec`
    The units need to be provided in descending order of magnitude.
    """
    # Configure logging.
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if verbose else logging.INFO
    )

    # Get domains from the environment variable.
    if domain_var := environ.get(DOMAINS_ENV_VAR, None):
        domains = list(domains)
        domains.extend(domain_var.split(" "))

    ApplicationJob(delay, token, domains).launch()


# Main entrypoint
if __name__ == "__main__":
    start(auto_envvar_prefix=BASE_ENV_VAR)
