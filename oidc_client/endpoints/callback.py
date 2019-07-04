"""Callback Endpoint."""

from aiohttp import web
from ..utils.utils import get_from_session
from ..utils.logging import LOG


async def callback_request(request):
    """Handle callback requests."""
    LOG.debug('Handle callback request.')
    # LOG.debug(request)
    state = await get_from_session(request, 'state')
    LOG.debug(f'from ses: {state}')

    # LOG.debug(f'from req: {request.rel_url.get('state')}')

    # return web.Response(body=f'state: {str(state)}')
    LOG.debug(request)
    LOG.debug(request.cookies)
    LOG.debug(request.remote)
    return web.Response(body='OK')
