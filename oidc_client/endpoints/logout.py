"""Logout Endpoint."""

from aiohttp import web

from ..utils.logging import LOG

async def logout_request(request):
    """Handle logout requests."""
    LOG.debug('Handle logout request.')

    raise web.HTTPNotImplemented()
