"""OIDC Client Web Server."""

import sys

from aiohttp import web
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from .endpoints.login import login_request
from .endpoints.logout import logout_request
from .endpoints.callback import callback_request
from .endpoints.token import token_request
from .config import CONFIG, LOG

routes = web.RouteTableDef()


@routes.get("/")
async def index(request: web.Request) -> web.Response:
    """Greeting endpoint."""
    return web.Response(body=CONFIG.app["name"])


@routes.get("/login")
async def login(request: web.Request):
    """Log user in by authenticating at AAI Server."""
    LOG.info("Received request to GET /login.")
    await login_request(request)


@routes.get("/logout")
async def logout(request: web.Request):
    """Log user out by destroying session at oidc-client and revoking access token at AAI server."""
    LOG.info("Received request to GET /logout.")
    await logout_request(request)


@routes.get("/callback")
async def callback(request: web.Request):
    """Receive callback from AAI server after authentication."""
    LOG.info("Received request to GET /callback.")
    await callback_request(request)


@routes.get("/token")
async def token(request: web.Request) -> web.Response:
    """Display token from session storage or cookies."""
    LOG.info("Received request to GET /token.")
    access_token = await token_request(request)
    return web.json_response({"access_token": access_token})


async def init() -> web.Application:
    """Initialise web server."""
    LOG.info("Initialise web server.")

    # Initialise server object
    server = web.Application()

    # Create encrypted session storage
    # Encryption key must be 32 len bytes
    session_setup(server, EncryptedCookieStorage(CONFIG.app["session_key"].encode()))

    # Gather endpoints
    server.router.add_routes(routes)

    return server


def main() -> None:
    """Start web server."""
    LOG.info("Start web server.")
    web.run_app(init(), host=CONFIG.app["host"], port=CONFIG.app["port"], shutdown_timeout=0)


if __name__ == "__main__":
    LOG.info("Starting OIDC Client Web API.")
    if sys.version_info < (3, 6):
        LOG.error("oidc-client requires python 3.6+")
        sys.exit(1)
    main()
