"""General Utility Functions."""

import os
import ssl

from uuid import uuid4

import aiohttp

from aiohttp import web
from aiocache import cached
from aiocache.serializers import JsonSerializer
from authlib.jose import jwt
from authlib.jose.errors import MissingClaimError, InvalidClaimError, ExpiredTokenError, BadSignatureError

from ..config import CONFIG
from .logging import LOG


def ssl_context(cert, key):
    """Handle application security."""
    LOG.debug('Load SSL context.')

    context = None
    if os.path.isfile(cert) and os.path.isfile(key):
        LOG.debug('Found SSL cert and key, serve app as HTTPS.')
        context = ssl.create_default_context()
        context.load_cert_chain(cert, key)

    # Debug log for start-up
    if context is None:
        LOG.debug(f'Certfile: {os.path.isfile(cert)}. Keyfile: {os.path.isfile(key)}.')
        LOG.debug('Empty SSL context, serve app as HTTP.')

    return None


async def generate_state():
    """Generate a state for authentication request and return the value for use."""
    LOG.debug('Generate a new state for authentication request.')
    return str(uuid4())


async def get_from_cookies(request, key):
    """Get a desired value from cookies."""
    LOG.debug(f'Retrieve value for {key} from cookies.')

    try:
        LOG.debug(f'Returning cookie value for: {key}.')
        return request.cookies[key]
    except KeyError as e:
        LOG.error(f'Cookies has no value for {key}: {e}.')
        raise web.HTTPUnauthorized(text='401 Uninitialised session.')
    except Exception as e:
        LOG.error(f'Failed to retrieve cookie: {e}')
        raise web.HTTPInternalServerError(text=f'500 Session has failed: {e}')


async def save_to_cookies(response, key='key', value='value', http_only=True, lifetime=300):
    """Save a given value to cookies."""
    LOG.debug(f'Save a value for {key} to cookies.')

    response.set_cookie(key,
                        value,
                        domain=CONFIG.cookie['domain'],
                        max_age=lifetime,
                        secure=CONFIG.cookie['secure'],
                        httponly=http_only)

    return response


async def request_token(code):
    """Request token from AAI."""
    LOG.debug('Requesting token.')

    auth = aiohttp.BasicAuth(login=CONFIG.aai['client_id'], password=CONFIG.aai['client_secret'])
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': CONFIG.aai['url_callback']
    }

    # Set up client authentication for request
    async with aiohttp.ClientSession(auth=auth) as session:
        # Send request to AAI
        async with session.post(CONFIG.aai['url_token'], data=data) as response:
            LOG.debug(f'AAI response status: {response.status}.')
            # Validate response from AAI
            if response.status == 200:
                # Parse response
                result = await response.json()
                # Look for access token
                if 'access_token' in result:
                    LOG.debug('Access token received.')
                    return result['access_token']
                else:
                    LOG.error('AAI response did not contain an access token.')
                    raise web.HTTPBadRequest(text='AAI response did not contain an access token.')
            else:
                LOG.error(f'Token request to AAI failed: {response}.')
                LOG.error(await response.json())
                raise web.HTTPBadRequest(text=f'Token request to AAI failed: {response.status}.')


async def query_params(request):
    """Parse query string params from path."""
    LOG.debug('Parse query params from AAI response.')

    # Response from AAI must have the query params `state` and `code`
    if 'state' in request.query and 'code' in request.query:
        LOG.debug('AAI response contained the correct params.')
        return {'state': request.query['state'], 'code': request.query['code']}
    else:
        LOG.error(f'AAI response is missing mandatory params, received: {request.query}')
        raise web.HTTPBadRequest(text='AAI response is missing mandatory parameters.')


async def check_bona_fide(token):
    """Check if user is recognised as a Bona Fide researcher.

    Bona Fide status is based on GA4GH RI claims specified in
    https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/RI_Claims_V1.md

    The exact requirements are described in
    https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/RI_Claims_V1.md#registered-access
    """
    LOG.debug('Checking Bona Fide status.')

    terms = False
    status = False
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        # Send request to AAI
        async with session.get(CONFIG.aai['url_userinfo'], headers=headers) as response:
            LOG.debug(f'AAI response status: {response.status}.')
            # Validate response from AAI
            if response.status == 200:
                # Parse response
                result = await response.json()
                # Check for Bona Fide values
                ga4gh = result.get('ga4gh', {})
                if 'AcceptedTermsAndPolicies' in ga4gh:
                    for accepted_terms in ga4gh["AcceptedTermsAndPolicies"]:
                        if accepted_terms.get("value") == CONFIG.elixir['bona_fide_value']:
                            terms = True
                if 'ResearcherStatus' in ga4gh:
                    for researcher_status in ga4gh["ResearcherStatus"]:
                        if researcher_status.get("value") == CONFIG.elixir['bona_fide_value']:
                            status = True
                if terms and status:
                    # User has agreed to terms and has been recognized by a peer, return True for Bona Fide status
                    return True
                else:
                    return False
            else:
                LOG.error(f'Userinfo request to AAI failed: {response}.')
                LOG.error(await response.json())
                raise web.HTTPBadRequest(text=f'Token request to AAI failed: {response.status}.')


@cached(ttl=3600, key="jwk", serializer=JsonSerializer())
async def get_jwk():
    """Get a key to decode access token with."""
    LOG.debug('Retrieving JWK.')

    # JWK can be fetched from environment instead of a server
    key = os.environ.get('JWK', None)
    if key is not None:
        return key

    # In other case, retrieve JWK from server
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CONFIG.aai['jwk_server']) as r:
                # This can be a single key or a list of JWK
                return await r.json()
    except Exception as e:
        LOG.error(f'Could not retrieve JWK: {e}')
        raise web.HTTPInternalServerError(text="Could not retrieve public key.")


async def validate_token(token):
    """Validate JWT."""
    LOG.debug('Validating access token.')

    # Get JWK to decode the token with
    jwk = await get_jwk()

    # Claims that must exist in the token, and required values if specified
    claims_options = {
        "iss": {
            "essential": True,
            "values": CONFIG.aai['iss'].split(',')  # Token allowed from these issuers
        },
        "aud": {
            "essential": True,
            "values": CONFIG.aai['aud'].split(',')  # Token allowed for these audiences
        },
        "iat": {
            "essential": True
        },
        "exp": {
            "essential": True
        }
    }
    try:
        # Decode the token and validate the contents
        decodedData = jwt.decode(token, jwk, claims_options=claims_options)
        decodedData.validate()
    except MissingClaimError as e:
        raise web.HTTPUnauthorized(text=f'Could not validate access token: Missing claim(s): {e}')
    except ExpiredTokenError as e:
        raise web.HTTPUnauthorized(text=f'Could not validate access token: Expired signature: {e}')
    except InvalidClaimError as e:
        raise web.HTTPForbidden(text=f'Could not validate access token: Token info not corresponding with claim: {e}')
    except BadSignatureError as e:
        raise web.HTTPForbidden(text=f'Could not validate access token: Token signature could not be verified: {e}')
