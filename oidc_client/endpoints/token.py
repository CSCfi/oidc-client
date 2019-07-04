"""Token Endpoint."""

from aiohttp import web

from ..utils.logging import LOG


async def token_request(request):
    """Handle token requests."""
    LOG.debug('Handle token request.')

    raise web.HTTPNotImplemented()
