import asynctest

from collections import namedtuple
# from ssl import SSLContext
from unittest.mock import MagicMock  # , patch

from aiohttp import web
from aioresponses import aioresponses
# from testfixtures import TempDirectory

from multidict import MultiDict

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


class TestUtils(asynctest.TestCase):
    """Test supporting utility functions."""

    # @patch('os.path.isfile')  # add m_os to params
    def test_ssl_context(self):
        """Test ssl context."""
        # Could not figure out how to mock load_cert_chain(), figure it out later
        # Test for ssl context loaded
        # with TempDirectory() as d:
        #     d.write('cert.pem', b'certfile')
        #     d.write('key.pem', b'keyfile')
        #     m_os.return_value = True
        #     self.assertTrue(isinstance(ssl_context('cert.pem', 'key.pem'), SSLContext))
        #     d.cleanup()
        # Test for ssl context not loaded, files are missing
        assert ssl_context('/missing/cert.pem', '/missing/key.pem') is None

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
        mandatory_params = {'state': 'happy', 'code': '123'}
        request = MagicMock()
        request.query = MultiDict([('code', '123'), ('state', 'happy'), ('add', 3)])

        parsed_params = await query_params(request)

        assert parsed_params == mandatory_params
        # Test missing mandatory params
        miss_request = MagicMock()
        miss_request.query = MultiDict([('missing', 'sad')])
        with self.assertRaises(web.HTTPBadRequest):
            await query_params(miss_request)

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
