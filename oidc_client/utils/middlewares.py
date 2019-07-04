"""API Middlewares."""

from aiohttp import web
from aiohttp_session import get_session

from .logging import LOG


def user_session():
    """Manage user session."""
    LOG.debug('Detecting user session.')

    @web.middleware
    async def user_session_middleware(request, handler):
        """Handle user session."""
        LOG.debug('Handling user session.')

        # Check if user has an active session
        session = await get_session(request)
        LOG.debug(session)

        return await handler(request)

    return user_session_middleware
