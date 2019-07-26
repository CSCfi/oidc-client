import asynctest

from aiohttp import web

from oidc_client.endpoints.login import login_request
from oidc_client.endpoints.logout import logout_request
# from oidc_client.endpoints.callback import callback_request


class TestEndpoints(asynctest.TestCase):
    """Test endpoint processors."""

    # Tests to do for login processor:
    # 1. Mock generate_state()
    # 2. Mock web.HTTPSeeOther()
    # 3. Mock save_to_cookies()
    # 4. Test that 303 is raised with generated url
    # 5. Test that response contains saved cookies
    async def test_login_endpoint(self):
        """Test login endpoint processor."""
        with self.assertRaises(web.HTTPSeeOther):
            await login_request({})

    async def test_logout_endpoint(self):
        """Test logout endpoint processor."""
        # logout endpoint is not yet implemented,
        # added scaffolding here for future test
        with self.assertRaises(web.HTTPNotImplemented):
            await logout_request({})

    # Tests to do for callback processor:
    # 1. Mock state from get_from_cookies()
    # 2. Mock params from query_params()
    # 3. Test for good state and bad state (OK and 401)
    # 4. Mock token from request_token()
    # 5. Test that 303 is raised with url
    # 6. Mock bona fide status from check_bona_fide()
    # 7. Mock save_to_cookies()
    # 8. Test that response contains saved cookies
    # async def test_callback_endpoint(self):
    #     """Test callback endpoint processor."""
    #     with self.assertRaises(web.HTTPSeeOther):
    #         await callback_request({})


if __name__ == '__main__':
    asynctest.main()
