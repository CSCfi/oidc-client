"""Token Endpoint."""

from aiohttp import web

from ..utils.utils import get_from_session
from ..utils.logging import LOG
from ..config import CONFIG


async def token_request(request):
    """Handle token requests."""
    LOG.debug('Handle token request.')

    # Get access token from session storage
    access_token = await get_from_session(request, 'access_token')

    return access_token
