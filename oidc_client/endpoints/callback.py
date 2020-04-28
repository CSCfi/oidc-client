"""Callback Endpoint."""

from aiohttp import web

from ..utils.utils import get_from_cookies, request_token, query_params, validate_token
from ..utils.logging import LOG


async def callback_request(request):
    """Handle callback requests."""
    LOG.debug('Handle callback request.')

    # Read saved state from cookies
    state = await get_from_cookies(request, 'oidc_state')
    # Parse authorised state from AAI response
    params = await query_params(request)

    # Verify, that states match
    if not state == params['state']:
        raise web.HTTPForbidden(text='403 Bad user session.')

    # Request access token from AAI server
    access_token = await request_token(params['code'])

    # Validate access token
    await validate_token(access_token)

    # Return access token
    return web.json_response({'access_token': access_token})
