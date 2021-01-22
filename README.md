# Cloudflare DDNS

![Linting](https://github.com/Akarys42/cloudflare-ddns-docker/workflows/Linting/badge.svg)
![Push Container](https://github.com/Akarys42/cloudflare-ddns-docker/workflows/Push%20Container/badge.svg)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)


Cloudflare DDNS is a configurable Docker service updating your CloudFlare DNS records periodically 
to match your local IP address. 

# Table of Content

- [Installation](#installation)
    - [Using a Pre-built Container](#using-a-pre-built-container)
    - [Building the Container Yourself](#building-the-container-yourself)
    - [Running on the Host](#running-on-the-host)
- [Configuration](#configuration)
    - [Getting a Cloudflare Token](#getting-a-cloudflare-token)
    - [Supported Options](#supported-options)
- [Contributing](#contributing)


## Installation

While this project is intended to be ran as a Docker container, it can also be ran on the host directly.

### Using a Pre-built Container

This project is available on the GitHub Container Registry.
```
docker pull ghcr.io/akarys42/cloudflare-ddns-docker
```

### Building the Container Yourself

There are no special requirements when building this container! Simply use `docker build` in this folder.

### Running on the Host

In order to run this project on the host, you'll need Python > 3.8, and an environment containing
the dependencies listed in [`requirements.txt`](requirements.txt). 

The project can then by launched by running the `cloudflare_ddns` module, usually using `python -m cloudflare_ddns`.


## Configuration

This project will accept parameters through environment variables or command line argument.
Feel free to select the method fitting your setup the best!

### Getting a Cloudflare Token

The first step will be to create an API token with the following scopes:
- `Zone:Read`
- `DNS:Edit`

### Supported Options

We currently support following settings:

| Parameter Name             | Short Command Line Option | Long Command Line Option | Environment Variable | Description                                                                                 |
|----------------------------|---------------------------|--------------------------|----------------------|---------------------------------------------------------------------------------------------|
| Token [mandatory]          | `-k`                      | `--token`                | `CF_DDNS_TOKEN`      | Your Cloudflare token created in the previous step.                                         |
| Delay [default: 5 minutes] | `-d`                      | `--delay`                | `CF_DDNS_DELAY`      | The time to wait between each update. It is parsed per [`strftime`](https://strftime.org/). |

The domains to update will have to either be passed as command line arguments after the options
or with a space separated `CF_DDNS_DOMAINS` environment variable.

Each domain can be preceded by the record type, either A or AAAA, followed by a colon.
Otherwise any found A or AAAA record pointing to this domain found will be used.

## Contributing

Any help would be greatly appreciated! 
Feel free to check our [open issues](https://github.com/Akarys42/cloudflare-ddns-docker/issues) and send us a Pull Request!
