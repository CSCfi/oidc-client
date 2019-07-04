"""Login Endpoint."""

import urllib.parse

from aiohttp import web

from ..utils.utils import generate_state
from ..utils.logging import LOG
from ..config import CONFIG


async def login_request(request):
    """Handle login requests."""
    LOG.debug('Handle login request.')

    # Create parameters for authorisation request
    params = {
        'client_id': CONFIG.aai['client_id'],
        'response_type': 'code',
        'state': await generate_state(request),
        'redirect_uri': CONFIG.aai['url_callback'],
        'duration': 'temporary',
        'scope': ' '.join(CONFIG.aai['scope'].split(','))
    }

    # Craft authorisation URL
    url = f"{CONFIG.aai['url_auth']}?{urllib.parse.urlencode(params)}"

    # raise web.HTTPFound('localhost:8000/callback')
    # Redirect user to remote AAI server for authentication, this does a 302 redirect
    raise web.HTTPFound(url)
