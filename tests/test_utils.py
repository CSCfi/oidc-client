import re

import asynctest

from collections import namedtuple
from unittest.mock import MagicMock

from aiohttp import web
from aioresponses import aioresponses
from authlib.jose import jwt

from multidict import MultiDict

from oidc_client.utils.utils import generate_state, get_from_cookies, save_to_cookies
from oidc_client.utils.utils import request_token, query_params, get_jwk, validate_token
from oidc_client.utils.utils import revoke_token

# Mock URLs in functions to replace the real request, checks for http/https/localhost in the beginning
MOCK_URL = re.compile(r'^(http|localhost)')


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


def mock_token(iss=None, aud=None, iat=None, exp=None):
    """Mock ELIXIR AAI token."""
    pem = {
        "kty": "oct",
        "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
        "use": "sig",
        "alg": "HS256",
        "k": "hJtXIZ2uSN5kbQfbtTNWbpdmhkV8FJG-Onbc6mxCcYg"
    }
    header = {
        "jku": "https://login.elixir-czech.org/oidc/jwk",
        "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
        "alg": "HS256"
    }
    payload = {
        "sub": "smth@elixir-europe.org"
    }
    if iss is not None:
        payload["iss"] = iss
    if aud is not None:
        payload["aud"] = aud
    if iat is not None:
        payload["iat"] = iat
    if exp is not None:
        payload["exp"] = exp
    token = jwt.encode(header, payload, pem).decode('utf-8')
    return token, pem


class TestUtils(asynctest.TestCase):
    """Test supporting utility functions."""

    async def test_generate_state(self):
        """Test state generation."""
        state = await generate_state()
        assert type(state) == str
        assert len(state) == 64

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
        m.post(MOCK_URL, status=200, payload={'access_token': 'secret'})
        token = await request_token("123")
        assert token == 'secret'
        # Test request OK, but token not received
        m.post(MOCK_URL, status=200, payload={})
        with self.assertRaises(web.HTTPBadRequest):
            await request_token("123")
        # Test failed request
        m.post(MOCK_URL, status=400)
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
    async def test_get_jwk(self, m):
        """Test getting JWK."""
        # Test getting key from server
        m.get(MOCK_URL, status=200, payload={'hello': 'there'})
        key = await get_jwk()
        self.assertEqual({'hello': 'there'}, key)

    @asynctest.mock.patch('oidc_client.utils.utils.get_jwk')
    async def test_validate_token(self, m_jwk):
        """Test token validation."""
        # Test token passes (raises no exceptions)
        token, pem = mock_token(iss='https://login.elixir-czech.org/oidc/',
                                aud='audience1',
                                iat=1111111111,
                                exp=9999999999)
        m_jwk.return_value = pem
        self.assertEqual(await validate_token(token), None)
        # Test for a missing claim
        token, pem = mock_token(iss='https://login.elixir-czech.org/oidc/',
                                aud='audience1',
                                exp=9999999999)
        m_jwk.return_value = pem
        with self.assertRaises(web.HTTPUnauthorized):
            await validate_token(token)
        # Test for expired token
        token, pem = mock_token(iss='https://login.elixir-czech.org/oidc/',
                                aud='audience1',
                                iat=1111111111,
                                exp=1111111111)
        m_jwk.return_value = pem
        with self.assertRaises(web.HTTPUnauthorized):
            await validate_token(token)
        # Test for invalid claim value
        token, pem = mock_token(iss='https://login.elixir-czech.org/oidc/',
                                aud='wrong_audience',
                                iat=1111111111,
                                exp=9999999999)
        m_jwk.return_value = pem
        with self.assertRaises(web.HTTPForbidden):
            await validate_token(token)
        # Test for bad key/signature
        token, _ = mock_token(iss='https://login.elixir-czech.org/oidc/',
                              aud='audience1',
                              iat=1111111111,
                              exp=9999999999)
        m_jwk.return_value = 'another key'
        with self.assertRaises(web.HTTPForbidden):
            await validate_token(token)

    @aioresponses()
    async def test_revoke_token(self, m):
        """Test token revocation."""
        # Test successful revocation of token
        m.get(MOCK_URL, status=200)
        await revoke_token('token')
        # Test failed revocation of token
        m.get(MOCK_URL, status=400)
        with self.assertRaises(web.HTTPBadRequest):
            await revoke_token('what')


if __name__ == '__main__':
    asynctest.main()
