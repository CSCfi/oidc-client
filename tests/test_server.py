import unittest
import asynctest

from unittest import mock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from oidc_client.app import init, main


class AppTestCase(AioHTTPTestCase):
    """Test endpoints."""

    async def get_application(self):
        """Retrieve web application for test."""
        return await init()

    @unittest_run_loop
    async def test_index(self):
        """Test root endpoint."""
        resp = await self.client.request("GET", "/")
        assert 200 == resp.status
        assert "oidc-client" == await resp.text()

    @asynctest.mock.patch("oidc_client.app.login_request", side_effect={})
    @unittest_run_loop
    async def test_login(self, mock_login):
        """Test login endpoint."""
        await self.client.request("GET", "/login")
        mock_login.assert_called()

    @asynctest.mock.patch("oidc_client.app.logout_request", side_effect={})
    @unittest_run_loop
    async def test_logout(self, mock_logout):
        """Test logout endpoint."""
        await self.client.request("GET", "/logout")
        mock_logout.assert_called()

    @asynctest.mock.patch("oidc_client.app.callback_request", side_effect={})
    @unittest_run_loop
    async def test_callback(self, mock_callback):
        """Test callback endpoint."""
        await self.client.request("GET", "/callback")
        mock_callback.assert_called()

    @asynctest.mock.patch("oidc_client.app.token_request", return_value="token")
    @unittest_run_loop
    async def test_token(self, mock_token):
        """Test token endpoint."""
        response = await self.client.request("GET", "/token")
        self.assertEqual(response.status, 200)
        self.assertEqual(await response.json(), {"access_token": "token"})


class TestBasicFunctionsApp(unittest.TestCase):
    """Test web app."""

    def setUp(self):
        """Initialise fixtures."""
        pass

    def tearDown(self):
        """Remove setup variables."""
        pass

    @mock.patch("oidc_client.app.web")
    def test_main(self, mock_web):
        """Should start the webapp."""
        main()
        mock_web.run_app.assert_called()

    async def test_init(self):
        """Test init type."""
        server = await init()
        self.assertIs(type(server), web.Application)


if __name__ == "__main__":
    unittest.main()
