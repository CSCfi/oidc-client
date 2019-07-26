import asynctest

from collections import namedtuple
from unittest.mock import patch

from aiohttp import web
from aioresponses import aioresponses

from oidc_client.utils.utils import ssl_context, generate_state, get_from_cookies, save_to_cookies
from oidc_client.utils.utils import request_token, query_params, check_bona_fide


def mock_request_with_cookies(cookies):
    """Generate a mock request that contains cookies."""
    payload = {"cookies": cookies}
    return namedtuple("cookies", payload.keys())(*payload.values())


class MockResponse:
    """Mocked response class for testing cookies."""

    def __init__(self):
        """Initialise object."""
        self.cookies = {}

    def set_cookie(self, key, value, domain, max_age, secure, httponly):
        """Set a cookie."""
        self.cookies.update(
            {
                key: value,
                'domain': domain,
                'max_age': max_age,
                'secure': secure,
                'httponly': httponly
            }
        )

    def cookies(self):
        """Return cookies."""
        return self.cookies


class TestUtils(asynctest.TestCase):
    """Test supporting utility functions."""

    def test_ssl_context(self):
        """Test ssl context."""
        # ssl_context() function is not yet implemented,
        # added scaffolding here for future test
        assert ssl_context() is None

    async def test_generate_state(self):
        """Test state generation."""
        state = await generate_state()
        assert type(state) == str
        assert len(state) == 36

    async def test_get_from_cookies(self):
        """Test retrieving values from cookies by key."""
        request = mock_request_with_cookies({"flavour": "white chocolate"})
        # Test for cookie found
        cookie = await get_from_cookies(request, 'flavour')
        assert cookie == 'white chocolate'
        # Test for cookie not found
        # Raises a KeyError and then raises a 401 due to unitialised session
        with self.assertRaises(web.HTTPUnauthorized):
            await get_from_cookies(request, 'missing')
        # Test for unknown errors, e.g. request is malformed
        with self.assertRaises(web.HTTPInternalServerError):
            await get_from_cookies({}, '')

    async def test_save_to_cookies(self):
        """Test saving a value to cookies."""
        response = MockResponse()
        response_with_cookies = await save_to_cookies(response,
                                                      'summer',
                                                      'unbearable',
                                                      http_only=True,
                                                      lifetime=3600)
        expected_cookies = {
            'summer': 'unbearable',
            'domain': 'localhost:8080',
            'httponly': True,
            'max_age': 3600,
            'secure': True
        }
        assert response_with_cookies.cookies == expected_cookies

    @aioresponses()
    async def test_request_token(self, m):
        """Test token request."""
        # Test token received
        m.post('https://aai.org/token', status=200, payload={'access_token': 'secret'})
        token = await request_token("123")
        assert token == 'secret'
        # Test request OK, but token not received
        m.post('https://aai.org/token', status=200, payload={})
        with self.assertRaises(web.HTTPBadRequest):
            await request_token("123")
        # Test failed request
        m.post('https://aai.org/token', status=400)
        with self.assertRaises(web.HTTPBadRequest):
            await request_token("123")

    async def test_query_params(self):
        """Test parsing of query params."""
        # Test found mandatory params
        # mandatory_params = {'state': 'happy', 'code': '123'}
        # Figure out how to mock request.rel_url.query.items()
        # with patch.object(web.Request, 'rel_url', return_value={}) as mock_request:
        #     parsed_params = await query_params(mock_request)
        #     assert parsed_params == mandatory_params
        # Test missing mandatory params
        with patch.object(web.Request, 'rel_url', return_value={}) as mock_request:
            with self.assertRaises(web.HTTPBadRequest):
                await query_params(mock_request)

    @aioresponses()
    async def test_check_bona_fide(self, m):
        """Test checking of Bona Fide status."""
        # Bona fide OK
        payload = {
            'ga4gh': {
                'AcceptedTermsAndPolicies': [
                    {
                        'value': 'bona_fide'
                    }
                ],
                'ResearcherStatus': [
                    {
                        'value': 'bona_fide'
                    }
                ]
            }
        }
        m.get('https://aai.org/userinfo', status=200, payload=payload)
        bona_fide_status = await check_bona_fide("token")
        assert bona_fide_status is True
        # Bona fide not OK
        m.get('https://aai.org/userinfo', status=200, payload={})
        bona_fide_status = await check_bona_fide("token")
        assert bona_fide_status is False
        # Test failed request
        m.get('https://aai.org/userinfo', status=400)
        with self.assertRaises(web.HTTPBadRequest):
            await check_bona_fide("token")


if __name__ == '__main__':
    asynctest.main()
