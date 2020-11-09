import asynctest

from aiohttp import web

from oidc_client.endpoints.login import login_request
from oidc_client.endpoints.logout import logout_request
from oidc_client.endpoints.callback import callback_request
from oidc_client.endpoints.token import token_request

from oidc_client.utils.utils import save_to_cookies


class MockResponse:
    """Mocked response class for testing cookies."""

    def __init__(self):
        """Initialise object."""
        self.cookies = {}

    def set_cookie(self, key, value, domain, max_age, secure, httponly):
        """Set a cookie."""
        self.cookies.update({key: value, "domain": domain, "max_age": max_age, "secure": secure, "httponly": httponly})


class MockRequest:
    """Mocked request class for testing."""

    def __init__(self, query):
        """Initialise object."""
        self.query = query

    def get(self, key):
        """For session key."""
        return key


class MockRedirect(Exception):
    """Mocks HTTPException 303."""

    def __init__(self):
        """Initialise object."""


class TestEndpoints(asynctest.TestCase):
    """Test endpoint processors."""

    @asynctest.mock.patch("aiohttp.web.HTTPSeeOther")
    @asynctest.mock.patch("oidc_client.endpoints.login.save_to_session")
    @asynctest.mock.patch("oidc_client.endpoints.login.generate_state")
    async def test_login_endpoint(self, m_state, m_save, m_response):
        """Test login endpoint processor."""
        m_state.return_value = "5000"
        m_save.return_value = None
        m_response.return_value = MockRedirect()
        with self.assertRaises(MockRedirect):
            mock_request = MockRequest(query={})
            await login_request(mock_request)

    @asynctest.mock.patch("oidc_client.endpoints.logout.revoke_token")
    @asynctest.mock.patch("oidc_client.endpoints.logout.get_from_cookies")
    async def test_logout_endpoint(self, m_cookies, m_rtoken):
        """Test logout endpoint processor."""
        m_cookies.return_value = "token"
        m_rtoken.return_value = True
        # Test that logout redirects user
        with self.assertRaises(web.HTTPSeeOther):
            await logout_request({})

    @asynctest.mock.patch("oidc_client.endpoints.callback.save_to_session")
    @asynctest.mock.patch("oidc_client.endpoints.callback.get_from_session")
    @asynctest.mock.patch("oidc_client.endpoints.callback.validate_token")
    @asynctest.mock.patch("oidc_client.endpoints.callback.request_tokens")
    async def test_callback_endpoint(self, m_token, m_valid, m_session, m_save):
        """Test callback endpoint processor."""
        # Test bad request: request doesn't pass state validation
        m_session.return_value = 5000
        bad_request = MockRequest(query={"state": 9999, "code": "malicious bunnies"})
        with self.assertRaises(web.HTTPForbidden):
            await callback_request(bad_request)
        # Test good request: request passes state validation and does a redirect
        m_session.return_value = 5000
        good_request = MockRequest(query={"state": 5000, "code": "fluffy bunnies"})
        m_valid.return_value = True
        m_save.return_value = None
        m_token.return_value = {"access_token": "super.secret.token", "id_token": "hi"}
        with self.assertRaises(web.HTTPSeeOther):
            await callback_request(good_request)
        # Test that access token is saved
        mock_response = MockResponse()
        expected_cookies = {"access_token": "super.secret.token", "domain": "localhost:8080", "httponly": True, "max_age": 3600, "secure": True}
        tokens = await m_token()
        m_response_with_cookies = await save_to_cookies(mock_response, key="access_token", value=tokens["access_token"], lifetime=3600, http_only=True)
        assert m_response_with_cookies.cookies == expected_cookies

    @asynctest.mock.patch("oidc_client.endpoints.token.get_from_session")
    async def test_token_endpoint(self, m_session):
        """Test token endpoint processor."""
        m_session.return_value = "token"
        mock_request = MockRequest(query={})
        token = await token_request(mock_request)
        self.assertEqual(token, "token")


if __name__ == "__main__":
    asynctest.main()
