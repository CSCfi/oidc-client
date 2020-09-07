"""Callback Endpoint."""

import secrets

from aiohttp import web

from ..utils.utils import get_from_session, save_to_session, save_to_cookies, request_token, query_params, validate_token
from ..config import CONFIG, LOG


async def callback_request(request: web.Request) -> web.HTTPSeeOther:
    """Handle callback requests."""
    LOG.debug("Handle callback request.")

    # Read saved state from session storage
    state = await get_from_session(request, "oidc_state")

    # Parse authorised state from AAI response
    params = await query_params(request)

    # Verify, that states match
    if not secrets.compare_digest(str(state), str(params["state"])):
        raise web.HTTPForbidden(text="403 Bad user session.")

    # Request access token from AAI server
    access_token = await request_token(params["code"])

    # Validate access token
    await validate_token(access_token)

    # Save access token to session storage
    await save_to_session(request, key="access_token", value=access_token)

    # Prepare response
    response = web.HTTPSeeOther(CONFIG.aai["url_redirect"])

    # Save the received access token to cookies for later use
    response = await save_to_cookies(
        response, key="access_token", value=access_token, lifetime=CONFIG.cookie["token_lifetime"], http_only=CONFIG.cookie["http_only"]
    )

    # Save a logged-in cookie for UI purposes
    response = await save_to_cookies(response, key="logged_in", value="True", lifetime=CONFIG.cookie["token_lifetime"], http_only=False)

    # Redirect user to UI, this does a 303 redirect
    raise response
