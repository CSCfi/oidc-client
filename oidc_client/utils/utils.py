"""General Utility Functions."""

from uuid import uuid4

from aiohttp import web

from aiohttp_session import get_session

from .logging import LOG


def ssl_context():
    """Handle application security."""
    return None


async def generate_state(request):
    """Generate a state for authentication request and return the value for use."""
    LOG.debug('Generate a new state for authentication request.')

    # Get session object for manipulation
    session = await get_session(request)

    # Generate a state for authentication request and store it
    session['state'] = str(uuid4())

    return session['state']


async def get_from_session(request, value):
    """Get a desired value from session."""
    LOG.debug('Accessing user session.')

    # Access session object
    session = await get_session(request)

    try:
        LOG.debug(f'Returning session value for: {value}.')
        return session[value]
    except KeyError as e:
        LOG.error(f'Session has no value for {value}: {e}.')
        raise web.HTTPUnauthorized(text='Uninitialised session. Please restart your session.')
    except Exception as e:
        LOG.error(f'Session has failed: {e}')
        raise web.HTTPInternalServerError(text=f'Session has failed: {e}')
