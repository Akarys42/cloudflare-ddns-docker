import logging

import click

from .constants import DEFAULT_DELAY
from .utils import parse_duration, validate_bearer

log = logging.getLogger("ddns")


@click.command()
@click.option('--delay', '-d', default=DEFAULT_DELAY, show_default=True)
@click.option('--token', '-k', prompt="Enter your Cloudflare Token", hide_input=True, show_envvar=True)
@click.option('-v', '--verbose', is_flag=True, default=False)
def start(delay: str, token: str, verbose: int) -> None:
    """Main application entrypoint."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if verbose else logging.INFO
    )

    try:
        duration = parse_duration(delay)
    except ValueError as e:
        log.error(f"Failed to parse delay: {e}")
        log.error("Exiting with code 64.")
        exit(64)

    try:
        log.debug("Validating bearer token.")

        validate_bearer(token)
    except ValueError as e:
        log.error(f"Failed to valid bearer token: {e}")
        log.error("Exiting with code 64.")
        exit(64)
    else:
        log.info("Successfully validated the bearer token.")


# Main entrypoint
if __name__ == "__main__":
    start(auto_envvar_prefix="CF_DDNS")
