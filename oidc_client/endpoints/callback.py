"""Callback Endpoint."""

from ..utils.utils import get_from_session
from ..utils.logging import LOG


async def callback_request(request):
    """Handle callback requests."""
    LOG.debug('Handle callback request.')
    state = await get_from_session(request, 'state')
