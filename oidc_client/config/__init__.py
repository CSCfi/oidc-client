"""OIDC Client Configuration."""

import os
from configparser import ConfigParser
from collections import namedtuple


def parse_config_file(path):
    """Parse configuration file."""
    config = ConfigParser()
    config.read(path)
    config_vars = {
        'app': {
            'host': os.environ.get('HOST', config.get('app', 'host')) or '0.0.0.0',
            'port': os.environ.get('PORT', config.get('app', 'port')) or 8080,
            'name': os.environ.get('NAME', config.get('app', 'name')) or 'oidc-client'
        },
        'aai': {
            'client_id': os.environ.get('CLIENT_ID', config.get('aai', 'client_id')) or 'public',
            'client_secret': os.environ.get('CLIENT_SECRET', config.get('aai', 'client_secret')) or 'secret',
            'url_auth': os.environ.get('URL_AUTH', config.get('aai', 'url_auth')) or None,
            'url_token': os.environ.get('URL_TOKEN', config.get('aai', 'url_token')) or None,
            'url_callback': os.environ.get('URL_CALLBACK', config.get('aai', 'url_callback')) or None,
            'scope': os.environ.get('SCOPE', config.get('aai', 'scope')) or 'openid'
        },
        'elixir': {
            'bona_fide_value': os.environ.get('BONA_FIDE_VALUE', config.get('elixir', 'bona_fide_value')) or ''
        }
    }
    return namedtuple("Config", config_vars.keys())(*config_vars.values())


CONFIG = parse_config_file(os.environ.get('CONFIG_FILE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')))