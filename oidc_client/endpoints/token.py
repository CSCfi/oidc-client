"""Token Endpoint."""

from aiohttp import web

from ..utils.utils import get_from_cookies
from ..config import CONFIG
from ..utils.logging import LOG


async def token_request(request):
    """Handle token requests."""
    LOG.debug('Handle token request.')

    # Read access token from cookies
    access_token = await get_from_cookies(request, 'access_token')

    # Return token to user
    return web.json_response({'access_token': access_token})
