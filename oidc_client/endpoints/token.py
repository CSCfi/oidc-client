"""Token Endpoint."""

from aiohttp import web

from ..utils.utils import get_from_session
from ..config import LOG


async def token_request(request: web.Request) -> str:
    """Handle token requests."""
    LOG.debug('Handle token request.')

    # Get access token from session storage
    access_token = await get_from_session(request, 'access_token')

    return access_token
