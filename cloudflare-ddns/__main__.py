import logging

import click
from email_validator import EmailNotValidError, validate_email

from .utils import parse_duration, validate_bearer

DEFAULT_DELAY = "5 minutes"


@click.command()
@click.option('--delay', '-d', default=DEFAULT_DELAY, show_default=True)
@click.option('--email', '-u', prompt="Enter your Cloudflare Email address")
@click.option('--key', '-k', prompt="Enter your Cloudflare Auth key", hide_input=True)
def start(delay: str, email: str, key: str) -> None:
    """Main application entrypoint."""
    try:
        duration = parse_duration(delay)
    except ValueError as e:
        logging.error(f"Failed to parse delay: {e}")
        logging.error("Exiting with code 64.")
        exit(64)

    try:
        validate_email(email)
    except EmailNotValidError:
        logging.warning(f"The email address {email} don't seem valid. Do you have a typo?")

    try:
        validate_bearer(key)
    except ...:
        ...


# Main entrypoint
if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")

    start(auto_envvar_prefix="CF_DDNS")
