"""General Utility Functions."""

from uuid import uuid4

from aiohttp import web

from aiohttp_session import new_session, get_session

from .logging import LOG


def ssl_context():
    """Handle application security."""
    return None


async def start_session(request):
    """Start a new session for user."""
    LOG.debug('Start new session for user.')

    # Get session object for manipulation
    session = await new_session(request)

    # Generate a CSRF token for authentication request
    session['csrf'] = str(uuid4())


async def get_from_session(request, value):
    """Get a desired value from session."""
    LOG.debug('Accessing user session.')

    # Access session object
    session = await get_session(request)

    try:
        LOG.debug(f'Returning session value for: {value}.')
        return session[value]
    except KeyError as e:
        LOG.error(f'Session has no value for {value}.')
        raise web.HTTPInternalServerError(text='Session is missing requested key. Try restarting session.')
    except Exception as e:
        LOG.error(f'Session has failed: {e}')
        raise web.HTTPInternalServerError(text=f'Session has failed: {e}')
