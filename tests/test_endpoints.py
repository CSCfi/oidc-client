import asynctest

from unittest.mock import patch

from aiohttp import web

from oidc_client.endpoints.login import login_request
from oidc_client.endpoints.logout import logout_request
from oidc_client.endpoints.callback import callback_request

from oidc_client.utils.utils import save_to_cookies


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


class MockRequest:
    """Mocked request class for testing."""

    def __init__(self, cookies, query):
        """Initialise object."""
        self.cookies = cookies
        self.query = query


class TestEndpoints(asynctest.TestCase):
    """Test endpoint processors."""

    @patch('aiohttp.web.HTTPSeeOther')
    @patch('oidc_client.endpoints.login.generate_state')
    async def test_login_endpoint(self, m_state, m_response):
        """Test login endpoint processor."""
        m_state.return_value = 5000
        assert 5000 == m_state()
        m_response.return_value = MockResponse()
        # This test always passes
        # url = 'https://aai.org/auth?client_id=public&response_type=code&state=5000&redirect_uri=localhost:5000&scope=openid%20ga4gh'
        # assert m_response.called_with(url)
        expected_cookies = {
            'oidc_state': 5000,
            'domain': 'localhost:8080',
            'httponly': True,
            'max_age': 3600,
            'secure': True
        }
        m_response_with_cookies = await save_to_cookies(m_response(),
                                                        key='oidc_state',
                                                        value=m_state(),
                                                        lifetime=3600,
                                                        http_only=True)
        assert m_response_with_cookies.cookies == expected_cookies
        with self.assertRaises(web.HTTPSeeOther):
            await login_request(web.Request)

    @asynctest.mock.patch('oidc_client.endpoints.logout.revoke_token')
    @asynctest.mock.patch('oidc_client.endpoints.logout.get_from_cookies')
    async def test_logout_endpoint(self, m_cookies, m_rtoken):
        """Test logout endpoint processor."""
        m_cookies.return_value = 'token'
        m_rtoken.return_value = True
        # Test that logout redirects user
        with self.assertRaises(web.HTTPSeeOther):
            await logout_request({})

    @asynctest.mock.patch('oidc_client.endpoints.callback.validate_token')
    @asynctest.mock.patch('oidc_client.endpoints.callback.check_bona_fide')
    @asynctest.mock.patch('oidc_client.endpoints.callback.request_token')
    async def test_callback_endpoint(self, m_token, m_bona, m_valid):
        """Test callback endpoint processor."""
        # Test bad request: request doesn't pass state validation
        bad_request = MockRequest(
            cookies={'oidc_state': 5000},
            query={'state': 9999, 'code': 'malicious bunnies'}
        )
        with self.assertRaises(web.HTTPForbidden):
            await callback_request(bad_request)
        # Test good request: request passes state validation and does a redirect
        good_request = MockRequest(
            cookies={'oidc_state': 5000},
            query={'state': 5000, 'code': 'fluffy bunnies'}
        )
        m_valid.return_value = True
        m_token.return_value = 'super.secret.token'
        m_bona.return_value = True
        with self.assertRaises(web.HTTPSeeOther):
            await callback_request(good_request)
        # Test that access token is saved
        mock_response = MockResponse()
        expected_cookies = {
            'access_token': 'super.secret.token',
            'domain': 'localhost:8080',
            'httponly': True,
            'max_age': 3600,
            'secure': True
        }
        m_response_with_cookies = await save_to_cookies(mock_response,
                                                        key='access_token',
                                                        value=await m_token(),
                                                        lifetime=3600,
                                                        http_only=True)
        assert m_response_with_cookies.cookies == expected_cookies


if __name__ == '__main__':
    asynctest.main()
