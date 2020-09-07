"""General Utility Functions."""

import secrets
import urllib.parse

import aiohttp

from aiohttp_session import get_session
from aiohttp import web
from aiocache import cached
from aiocache.serializers import JsonSerializer
from authlib.jose import jwt
from authlib.jose.errors import MissingClaimError, InvalidClaimError, ExpiredTokenError, BadSignatureError

from ..config import CONFIG, LOG


async def generate_state() -> str:
    """Generate a state for authentication request and return the value for use."""
    LOG.debug("Generate a new state for authentication request.")
    return secrets.token_hex()


async def get_from_session(request: web.Request, key: str) -> str:
    """Get a desired value from session storage."""
    LOG.debug(f"Retrieve value for {key} from session storage.")

    session = await get_session(request)
    try:
        LOG.debug(f"Returning session value for: {key}.")
        return session[key]
    except KeyError as e:
        LOG.error(f"Session has no value for {key}: {e}.")
        raise web.HTTPUnauthorized(text="401 Uninitialised session.")
    except Exception as e:
        LOG.error(f"Failed to retrieve {key} from session: {e}")
        raise web.HTTPInternalServerError(text=f"500 Session has failed: {e}")


async def save_to_session(request: web.Request, key: str = "key", value: str = "value") -> None:
    """Save a given value to a session key."""
    LOG.debug(f"Save a value for {key} to session.")

    session = await get_session(request)
    session[key] = value


async def get_from_cookies(request: web.Request, key: str) -> str:
    """Get a desired value from cookies."""
    LOG.debug(f"Retrieve value for {key} from cookies.")

    try:
        LOG.debug(f"Returning cookie value for: {key}.")
        return request.cookies[key]
    except KeyError as e:
        LOG.error(f"Cookies has no value for {key}: {e}.")
        raise web.HTTPUnauthorized(text="401 Uninitialised session.")
    except Exception as e:
        LOG.error(f"Failed to retrieve cookie: {e}")
        raise web.HTTPInternalServerError(text=f"500 Session has failed: {e}")


async def save_to_cookies(response: web.HTTPSeeOther, key: str = "key", value: str = "value", http_only=True, lifetime: int = 300) -> web.HTTPSeeOther:
    """Save a given value to cookies."""
    LOG.debug(f"Save a value for {key} to cookies.")

    response.set_cookie(key, value, domain=CONFIG.cookie["domain"], max_age=lifetime, secure=CONFIG.cookie["secure"], httponly=http_only)

    return response


async def request_token(code: str) -> str:
    """Request token from AAI."""
    LOG.debug("Requesting token.")

    auth = aiohttp.BasicAuth(login=CONFIG.aai["client_id"], password=CONFIG.aai["client_secret"])
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": CONFIG.aai["url_callback"]}

    # Set up client authentication for request
    async with aiohttp.ClientSession(auth=auth) as session:
        # Send request to AAI
        async with session.post(CONFIG.aai["url_token"], data=data) as response:
            LOG.debug(f"AAI response status: {response.status}.")
            # Validate response from AAI
            if response.status == 200:
                # Parse response
                result = await response.json()
                # Look for access token
                if "access_token" in result:
                    LOG.debug("Access token received.")
                    return result["access_token"]
                else:
                    LOG.error("AAI response did not contain an access token.")
                    raise web.HTTPBadRequest(text="AAI response did not contain an access token.")
            else:
                LOG.error(f"Token request to AAI failed: {response}.")
                LOG.error(await response.json())
                raise web.HTTPBadRequest(text=f"Token request to AAI failed: {response.status}.")


async def query_params(request: web.Request) -> dict:
    """Parse query string params from path."""
    LOG.debug("Parse query params from AAI response.")

    # Response from AAI must have the query params `state` and `code`
    if "state" in request.query and "code" in request.query:
        LOG.debug("AAI response contained the correct params.")
        return {"state": request.query["state"], "code": request.query["code"]}
    else:
        LOG.error(f"AAI response is missing mandatory params, received: {request.query}")
        raise web.HTTPBadRequest(text="AAI response is missing mandatory parameters.")


@cached(ttl=3600, key="jwk", serializer=JsonSerializer())
async def get_jwk() -> dict:
    """Get a key to decode access token with."""
    LOG.debug("Retrieving JWK.")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CONFIG.aai["jwk_server"]) as r:
                # This can be a single key or a list of JWK
                return await r.json()
    except Exception as e:  # pragma: no cover
        # cache is preventing the testing of this block. this block has been tested manually
        LOG.error(f"Could not retrieve JWK: {e}")
        raise web.HTTPInternalServerError(text="Could not retrieve public key.")


async def validate_token(token: str) -> None:
    """Validate JWT."""
    LOG.debug("Validating access token.")

    # Get JWK to decode the token with
    jwk = await get_jwk()

    # Claims that must exist in the token, and required values if specified
    claims_options = {
        "iss": {"essential": True, "values": CONFIG.aai["iss"].split(",")},  # Token allowed from these issuers
        "aud": {"essential": True, "values": CONFIG.aai["aud"].split(",")},  # Token allowed for these audiences
        "iat": {"essential": True},
        "exp": {"essential": True},
    }
    try:
        # Decode the token and validate the contents
        decoded_data = jwt.decode(token, jwk, claims_options=claims_options)
        decoded_data.validate()
    except MissingClaimError as e:
        raise web.HTTPUnauthorized(text=f"Could not validate access token: Missing claim(s): {e}")
    except ExpiredTokenError as e:
        raise web.HTTPUnauthorized(text=f"Could not validate access token: Expired signature: {e}")
    except InvalidClaimError as e:
        raise web.HTTPForbidden(text=f"Could not validate access token: Token info not corresponding with claim: {e}")
    except BadSignatureError as e:
        raise web.HTTPForbidden(text=f"Could not validate access token: Token signature could not be verified: {e}")


async def revoke_token(token: str) -> None:
    """Request token revocation at AAI."""
    LOG.debug("Revoking token.")

    auth = aiohttp.BasicAuth(login=CONFIG.aai["client_id"], password=CONFIG.aai["client_secret"])
    params = {"token": token}

    # Set up client authentication for request
    async with aiohttp.ClientSession(auth=auth) as session:
        # Send request to AAI
        async with session.get(f"{CONFIG.aai['url_revoke']}?{urllib.parse.urlencode(params)}") as response:
            LOG.debug(f"AAI response status: {response.status}.")
            # Validate response from AAI
            if response.status != 200:
                LOG.error(f"Logout failed at AAI: {response}.")
                LOG.error(await response.json())
                raise web.HTTPBadRequest(text=f"Logout failed at AAI: {response.status}.")
