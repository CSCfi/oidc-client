"""OIDC Client Web Server."""

import sys
import logging
import base64

from cryptography import fernet

from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from .endpoints.login import login_request
from .endpoints.logout import logout_request
from .endpoints.callback import callback_request
from .endpoints.token import token_request
from .utils.utils import ssl_context
from .config import CONFIG

FORMAT = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

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


def init():
    """Initialise web server."""
    # Initialise server object
    server = web.Application()
    # Setup an encrypted session storage for user data
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(server, EncryptedCookieStorage(secret_key))
    # Gather endpoints
    server.router.add_routes(routes)
    return server


def main():
    """Start web server."""
    web.run_app(init(),
                host=CONFIG.app['host'],
                port=CONFIG.app['port'],
                shutdown_timeout=0,
                ssl_context=ssl_context())


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        LOG.error("oidc-client requires python 3.6+")
        sys.exit(1)
    main()