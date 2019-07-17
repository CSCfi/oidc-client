"""OIDC Client Web Server."""

import sys

from aiohttp import web

from .endpoints.login import login_request
from .endpoints.logout import logout_request
from .endpoints.callback import callback_request
from .endpoints.token import token_request
from .utils.utils import ssl_context
from .utils.logging import LOG
from .config import CONFIG

routes = web.RouteTableDef()


@routes.get('/')
async def index(request):
    """Greeting endpoint."""
    return web.Response(body=CONFIG.app['name'])


@routes.get('/login')
async def login(request):
    """Log user in by authenticating at AAI Server."""
    LOG.info('Received request to GET /login.')
    await login_request(request)


@routes.get('/logout')
async def logout(request):
    """Log user out by destroying session at oidc-client and revoking access token at AAI server."""
    LOG.info('Received request to GET /logout.')
    await logout_request(request)


@routes.get('/callback')
async def callback(request):
    """Receive callback from AAI server after authentication."""
    LOG.info('Received request to GET /callback.')
    await callback_request(request)


@routes.get('/token')
async def token(request):
    """Return access token."""
    LOG.info('Received request to GET /token.')
    await token_request(request)


async def init():
    """Initialise web server."""
    LOG.info('Initialise web server.')

    # Initialise server object
    server = web.Application()

    # Gather endpoints
    server.router.add_routes(routes)

    return server


def main():
    """Start web server."""
    LOG.info('Start web server.')
    web.run_app(init(),
                host=CONFIG.app['host'],
                port=CONFIG.app['port'],
                shutdown_timeout=0,
                ssl_context=ssl_context())


if __name__ == '__main__':
    LOG.info('Starting OIDC Client Web API.')
    if sys.version_info < (3, 6):
        LOG.error('oidc-client requires python 3.6+')
        sys.exit(1)
    main()
