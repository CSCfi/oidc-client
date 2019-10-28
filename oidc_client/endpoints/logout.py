"""Logout Endpoint."""

from aiohttp import web

from ..utils.utils import get_from_cookies, revoke_token, save_to_cookies
from ..config import CONFIG
from ..utils.logging import LOG


async def logout_request(request):
    """Handle logout requests."""
    LOG.debug('Handle logout request.')

    # Read access token from cookies
    access_token = await get_from_cookies(request, 'access_token')

    # Revoke token at AAI
    await revoke_token(access_token)

    # Prepare response
    response = web.HTTPSeeOther(CONFIG.aai['url_redirect'])

    # Overwrite token cookie with an instantly expiring one
    response = await save_to_cookies(response,
                                     key='access_token',
                                     value='token_has_been_revoked',
                                     lifetime=0,
                                     http_only=CONFIG.cookie['http_only'])

    # Redirect user to UI, this does a 303 redirect
    raise response
