## OIDC Client

[![Build Status](https://travis-ci.org/CSCfi/oidc-client.svg?branch=master)](https://travis-ci.org/CSCfi/oidc-client)
[![Coverage Status](https://coveralls.io/repos/github/CSCfi/oidc-client/badge.svg)](https://coveralls.io/github/CSCfi/oidc-client)
[![Documentation Status](https://readthedocs.org/projects/csc-oidc-client/badge/?version=latest)](https://csc-oidc-client.readthedocs.io/en/latest/?badge=latest)

CSC OIDC Client is a lightweight [aiohttp](https://aiohttp.readthedocs.io/en/stable/) web application used for interacting with OIDC servers.
The source code is delivered with [ELIXIR AAI](https://elixir-europe.org/services/compute/aai) integration.

### Quick Start

`oidc-client` requires `python 3.6` or higher.

##### Download and Install

```
git clone https://github.com/CSCfi/oidc-client
cd oidc-client
pip install .
```

##### Run Application

After configuring OIDC Client in `oidc-client/oidc_client/config/config.ini` start a development server with.

```
# run installed python module
start_oidc_client

# run without installing
python -m oidc_client.app
```

##### Example Usage

Navigate to `localhost:8080/login` to authenticate at the configured AAI server. An access token in the format of a [JWT](https://tools.ietf.org/html/rfc7519) is saved to cookies upon a successful authentication procedure.

### Documentation

For more installation and production deployment instructions and examples see the [documentation](https://csc-oidc-client.readthedocs.io/en/latest/?badge=latest).
