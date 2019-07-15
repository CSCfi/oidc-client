"""General Utility Functions."""

from uuid import uuid4

import aiohttp

from aiohttp import web

from aiohttp_session import get_session, new_session

from ..config import CONFIG
from .logging import LOG


def ssl_context():
    """Handle application security."""
    return None


async def generate_state(request):
    """Generate a state for authentication request and return the value for use."""
    LOG.debug('Generate a new state for authentication request.')

    # Start a new session when user logs in
    await new_session(request)

    # Generate a state for authentication request
    state = str(uuid4())

    # Store state to user session
    await save_to_session(request, key='state', value=state)


async def get_from_session(request, key):
    """Get a desired value from session."""
    LOG.debug('Accessing user session to retrieve a value.')

    # Access session object
    session = await get_session(request)

    try:
        LOG.debug(f'Returning session value for: {key}.')
        return session[key]
    except KeyError as e:
        LOG.error(f'Session has no value for {key}: {e}.')
        raise web.HTTPUnauthorized(text='Incomplete session. Please restart your session.')
    except Exception as e:
        LOG.error(f'Session has failed: {e}')
        raise web.HTTPInternalServerError(text=f'Session has failed: {e}')


async def save_to_session(request, key='key', value='value'):
    """Save given value to key in session."""
    LOG.debug('Accessing user session to save a value.')

    # Access session object
    session = await get_session(request)

    # Save value to key
    session[key] = value


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
                LOG.error(f'Token request from AAI failed: {response}.')
                LOG.error(await response.json())
                raise web.HTTPBadRequest(text=f'Token request from AAI failed: {response.status}.')


async def query_params(request):
    """Parse query string params from path."""
    LOG.debug('Parse query params from AAI response.')

    desired_params = ['state', 'code']
    params = {k: v for k, v in request.rel_url.query.items() if k in desired_params}

    # Response from AAI must have the query params `state` and `code`
    if 'state' in params and 'code' in params:
        LOG.debug('AAI response contained the correct params.')
        return params
    else:
        LOG.error(f'AAI response is missing mandatory params, received: {params}')
        raise web.HTTPBadRequest(text='AAI response is missing mandatory parameters.')
