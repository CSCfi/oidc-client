"""Login Endpoint."""

import urllib.parse

from aiohttp import web

from ..utils.utils import get_from_session
from ..utils.logging import LOG
from ..config import CONFIG


async def login_request(request):
    """Handle login requests."""
    LOG.debug('Handle login request.')

    # Create parameters for authorisation request
    params = {
        'client_id': CONFIG.aai['client_id'],
        'response_type': 'code',
        'state': await get_from_session(request, 'csrf'),
        'redirect_uri': CONFIG.aai['url_callback'],
        'duration': 'temporary',
        'scope': CONFIG.aai['scope']
    }

    # Craft authorisation URL
    url = f"{CONFIG.aai['url_auth']}?{urllib.parse.urlencode(params)}"

    # Redirect user to remote AAI server for authentication
    raise web.HTTPFound(url)
