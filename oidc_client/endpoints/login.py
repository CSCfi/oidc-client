"""Login Endpoint."""

import urllib.parse

from aiohttp import web

from ..utils.utils import generate_state, save_to_cookies
from ..utils.logging import LOG
from ..config import CONFIG


async def login_request(request):
    """Handle login requests."""
    LOG.debug('Handle login request.')

    # Generate a state for callback
    state = await generate_state()

    # Create parameters for authorisation request
    params = {
        'client_id': CONFIG.aai['client_id'],
        'response_type': 'code',
        'state': state,
        'redirect_uri': CONFIG.aai['url_callback'],
        'scope': ' '.join(CONFIG.aai['scope'].split(','))
    }

    # Craft authorisation URL
    url = f"{CONFIG.aai['url_auth']}?{urllib.parse.urlencode(params)}"

    # Prepare response
    response = web.HTTPSeeOther(url)

    # Save state to cookies
    await save_to_cookies(response, key='oidc_state', value=state, lifetime=CONFIG.cookie['state_lifetime'])

    # Redirect user to remote AAI server for authentication, this does a 303 redirect
    return response
