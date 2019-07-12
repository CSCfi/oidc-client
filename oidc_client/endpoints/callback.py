"""Callback Endpoint."""

from aiohttp import web
from ..utils.utils import get_from_session, save_to_session, request_token, query_params
from ..utils.logging import LOG


async def callback_request(request):
    """Handle callback requests."""
    LOG.debug('Handle callback request.')

    # Read saved state from user session
    state = await get_from_session(request, 'state')
    # Parse authorised state from AAI response
    params = await query_params(request)

    # Verify, that states match
    if not state == params['state']:
        raise web.HTTPForbidden(text='Bad user session.')

    # Request access token from AAI server
    access_token = await request_token(params['code'])

    # Save the received access token to session for later use
    await save_to_session(request, key='access_token', value=access_token)

    return web.Response(body='Authentication completed. Later this will redirect the user to UI.')
