"""Callback Endpoint."""

import secrets

from aiohttp import web

from ..utils.utils import get_from_session, save_to_session, save_to_cookies, request_tokens, query_params, validate_token, revoke_token
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

    # Request id token and access token from AAI server
    tokens = await request_tokens(params["code"])

    # Validate tokens
    await validate_token(tokens["access_token"])
    await validate_token(tokens["id_token"])  # validated but not saved or used
    if CONFIG.aai["url_revoke"]:
        # Some OIDC OPs don't provide a logout endpoint, so we first check if it's configured before trying to revoke the token
        # We want to revoke the id_token because we don't use it for anything, and we don't want to leave user data hanging
        await revoke_token(tokens["id_token"])

    # Save access token to session storage
    await save_to_session(request, key="access_token", value=tokens["access_token"])

    # Prepare response
    response = web.HTTPSeeOther(CONFIG.aai["url_redirect"])

    # Save the received access token to cookies for later use
    response = await save_to_cookies(
        response, key="access_token", value=tokens["access_token"], lifetime=CONFIG.cookie["token_lifetime"], http_only=CONFIG.cookie["http_only"]
    )

    # Save a logged-in cookie for UI purposes
    response = await save_to_cookies(response, key="logged_in", value="True", lifetime=CONFIG.cookie["token_lifetime"], http_only=False)

    # Redirect user to UI, this does a 303 redirect
    raise response
