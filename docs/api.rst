API Endpoints
=============

OIDC Client consists of four endpoints: ``/``, ``/login``, ``/logout``, ``/callback``.

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

The logout endpoint ``/logout`` is used to destroy sessions cookies and invalidate the access token.

.. note:: ELIXIR AAI has not implemented a logout feature yet, so this feature is also missing from OIDC Client.

Callback
~~~~~~~~

The callback endpoint ``/callback`` acts as a landing site for the returning user from the AAI server.
Upon returning to the OIDC Client from the AAI server, OIDC Client extracts ``state`` and ``code`` from the callback request,
and uses these values to request a token from the AAI server. Upon a successful retrieval of an access token, the access token
is saved to the browser cookies.

Other cookies created cookies include unsafe cookies for the purpose of displaying values in UI for logged in state and bona fide status.

Cookies
~~~~~~~

Cookies created and used by the OIDC Client and their default settings.

+---------------+-----------+----------------------------------------------------+----------+--------+-----------+
| Cookie        | Origin    | Purpose                                            | Lifetime | Secure | Http Only |
+===============+===========+====================================================+==========+========+===========+
| oidc_state    | /login    | Store state at login to be checked upon callback   | 5 min    | True   | True      |
+---------------+-----------+----------------------------------------------------+----------+--------+-----------+
| access_token  | /callback | Sent along requests for authorizing access to data | 1 hour   | True   | True      |
+---------------+-----------+----------------------------------------------------+----------+--------+-----------+
| logged_in     | /callback | Used to display logged in state in UI              | 1 hour   | True   | False     |
+---------------+-----------+----------------------------------------------------+----------+--------+-----------+
| bona_fide     | /callback | Used to display bona fide status in UI             | 1 hour   | True   | False     |
+---------------+-----------+----------------------------------------------------+----------+--------+-----------+
