"""Token Endpoint."""

from aiohttp import web

from ..utils.utils import get_from_cookies
from ..config import LOG


async def token_request(request: web.Request) -> str:
    """Handle token requests."""
    LOG.debug("Handle token request.")

    # Get access token from cookies
    access_token = await get_from_cookies(request, "access_token")

    return access_token
