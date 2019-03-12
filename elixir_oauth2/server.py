from aiohttp import web
import logging
import os
import sys

FORMAT = '[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

routes = web.RouteTableDef()


@routes.get('/health')
async def healthcheck(request):
    """Test health, will always return ok."""
    LOG.debug('Healthcheck called')
    return web.Response(body='OK')


def init():
    """Initialise server."""
    server = web.Application()
    server.router.add_routes(routes)
    return server


def main():
    """Run the ELIXIR AAI OAuth2 Server."""
    # make it HTTPS and request certificate
    # sslcontext.load_cert_chain(ssl_certfile, ssl_keyfile)
    # sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # sslcontext.check_hostname = False
    web.run_app(init(), host=os.environ.get('HOST', '0.0.0.0'),
                port=os.environ.get('PORT', '6430'),
                shutdown_timeout=0, ssl_context=None)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), "ELIXIR AAI OAuth2 Service requires python3.6"
    main()
