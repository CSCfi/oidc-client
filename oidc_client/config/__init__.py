"""OIDC Client Configuration."""

import os
import secrets
import logging

from pathlib import Path
from configparser import ConfigParser
from collections import namedtuple
from distutils.util import strtobool

formatting = "[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(module)s | %(funcName)s: %(message)s"
logging.basicConfig(level=logging.DEBUG if bool(strtobool(os.environ.get("DEBUG", "False"))) else logging.INFO, format=formatting)
LOG = logging.getLogger("oidc")


def parse_config_file(path):
    """Parse configuration file."""
    config = ConfigParser()
    config.read(path)
    config_vars = {
        "app": {
            "host": os.environ.get("HOST", config.get("app", "host")) or "0.0.0.0",  # nosec
            "port": os.environ.get("PORT", config.get("app", "port")) or 8080,
            "name": os.environ.get("NAME", config.get("app", "name")) or "oidc-client",
            "session_key": os.environ.get("SESSION_KEY", config.get("app", "session_key")) or secrets.token_hex(16),
        },
        "cookie": {
            "domain": os.environ.get("DOMAIN", config.get("cookie", "domain")) or "localhost",
            "token_lifetime": int(os.environ.get("TOKEN_LIFETIME", config.get("cookie", "token_lifetime"))) or 3600,
            "state_lifetime": int(os.environ.get("STATE_LIFETIME", config.get("cookie", "state_lifetime"))) or 300,
            "secure": bool(strtobool(os.environ.get("SECURE", config.get("cookie", "secure")))) or True,
            "http_only": bool(strtobool(os.environ.get("HTTP_ONLY", config.get("cookie", "http_only")))) or True,
        },
        "aai": {
            "client_id": os.environ.get("CLIENT_ID", config.get("aai", "client_id")) or "public",
            "client_secret": os.environ.get("CLIENT_SECRET", config.get("aai", "client_secret")) or "secret",
            "url_auth": os.environ.get("URL_AUTH", config.get("aai", "url_auth")) or None,
            "url_token": os.environ.get("URL_TOKEN", config.get("aai", "url_token")) or None,
            "url_userinfo": os.environ.get("URL_USERINFO", config.get("aai", "url_userinfo")) or None,
            "url_callback": os.environ.get("URL_CALLBACK", config.get("aai", "url_callback")) or None,
            "url_redirect": os.environ.get("URL_REDIRECT", config.get("aai", "url_redirect")) or None,
            "url_revoke": os.environ.get("URL_REVOKE", config.get("aai", "url_revoke")) or None,
            "scope": os.environ.get("SCOPE", config.get("aai", "scope")) or "openid",
            "iss": os.environ.get("ISS", config.get("aai", "iss")) or None,
            "aud": os.environ.get("AUD", config.get("aai", "aud")) or None,
            "jwk_server": os.environ.get("JWK_SERVER", config.get("aai", "jwk_server")) or None,
        },
    }
    return namedtuple("Config", config_vars.keys())(*config_vars.values())


CONFIG = parse_config_file(os.environ.get("CONFIG_FILE", Path(__file__).resolve().parent.joinpath("config.ini")))
