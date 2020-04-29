"""Token Endpoint."""

from ..utils.utils import get_from_cookies
from ..config import CONFIG
from ..utils.logging import LOG


async def token_request(request):
    """Handle token requests."""
    LOG.debug('Handle token request.')

    # Read access token from cookies
    access_token = await get_from_cookies(request, 'access_token')

    # Return token to user
    return {'access_token': access_token}
