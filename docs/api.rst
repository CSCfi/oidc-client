API Endpoints
=============

OIDC Client consists of five endpoints: ``/``, ``/login``, ``/logout``, ``/callback`` and ``/token``.

.. _index:

Index
~~~~~

The index endpoint ``/`` is used as a healthcheck endpoint, it returns the name of the service as given in the configuration file.

Login
~~~~~

The login endpoint ``/login`` generates a state and saves this state to cookies, after which the user is redirected to the AAI server for authentication.
Upon a successful authentication at the AAI, the user is returned to the ``/callback`` endpoint.

Logout
~~~~~~

The logout endpoint ``/logout`` is used to destroy the access token cookie and to revoke the access token at the AAI.
Upon a successful logout procedure, the user is returned to the ``url_redirect`` address from the configuration file.

Callback
~~~~~~~~

The callback endpoint ``/callback`` acts as a landing site for the returning user from the AAI server.
Upon returning to the OIDC Client from the AAI server, OIDC Client extracts ``state`` and ``code`` from the callback request,
and uses these values to request a token from the AAI server. Upon a successful retrieval of an access token, the access token
is saved to the browser cookies.

Some of the created cookies can be considered _unsafe_ (not `http_only`) for the purpose of displaying values in UI for logged in state.

Token
~~~~~

Display token from encrypted session storage for easy retrieval. Alternate way to inspect the access token is to look at the browser cookies.

Cookies
~~~~~~~

Cookies created and used by the OIDC Client and their default settings.

+-----------------+-----------+---------------------------------------------------------------------------------------------------------------------+----------+--------+-----------+
| Cookie          | Origin    | Purpose                                                                                                             | Lifetime | Secure | Http Only |
+-----------------+-----------+---------------------------------------------------------------------------------------------------------------------+----------+--------+-----------+
| AIOHTTP_SESSION | /login    | Store state at login to be checked upon callback. Store access token at callback to be displayed at token endpoint. | Session  | True   | True      |
+-----------------+-----------+---------------------------------------------------------------------------------------------------------------------+----------+--------+-----------+
| access_token    | /callback | Sent along same-domain requests for authorizing access to data                                                      | 1 hour   | True   | True      |
+-----------------+-----------+---------------------------------------------------------------------------------------------------------------------+----------+--------+-----------+
| logged_in       | /callback | Used to display logged in state in UI                                                                               | 1 hour   | True   | False     |
+-----------------+-----------+---------------------------------------------------------------------------------------------------------------------+----------+--------+-----------+
