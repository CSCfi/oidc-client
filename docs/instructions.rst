Installation Instructions
=========================

.. note:: ``oidc-client`` requires python 3.6 or higher:

.. _dev-server:

Development Server
~~~~~~~~~~~~~~~~~~

For development, OIDC Client can be run without installation as a python module from the root folder ``/oidc-client``:

.. code-block:: console

    cd oidc-client
    python -m oidc_client.app

This starts the OIDC Client with ``aiohttp.web.run_app``.

.. _installation:

Installation
~~~~~~~~~~~~

OIDC Client can be installed into the python environment with ``pip install`` from the root folder ``/oidc-client``:

.. code-block:: console

    cd oidc-client
    pip install .

The server can then be started with the following command:

.. code-block:: console

    start_oidc_client

This starts the OIDC Client with ``aiohttp.web.run_app``.

.. _production-server:

Production Server
~~~~~~~~~~~~~~~~~

For production it is recommended to use `gunicorn <https://gunicorn.org/>`_ instead of aiohttp's default server for stability.

To start the production server, the web application must first be built, as described in the Installation section above.
The host and port must also be provided beforehand in environment variables:

.. code-block:: console

    export APP_HOST=0.0.0.0
    export APP_PORT=8080

The production server is started from the root folder ``/oidc-client`` with:

.. code-block:: console

    gunicorn oidc_client.app:init --bind $APP_HOST:$APP_PORT \
                                  --worker-class aiohttp.GunicornUVLoopWebWorker \
                                  --workers 4

.. _container-deployment:

Container Deployment
~~~~~~~~~~~~~~~~~~~~

OIDC Client can also be built into a container and then be deployed.
Builds must be initiated from the root folder ``/oidc-client``.

To build OIDC Client into an image using ``s2i``:

.. code-block:: console

    s2i build . centos/python-36-centos7 cscfi/oidc-client

To run the built image with docker:

.. code-block:: console

    docker run -d -p 8080:8080 cscfi/oidc-client
