Configuration
=============

OIDC Client has three configuration levels, that take priority from top to bottom:

* Environment Variable
* Configuration File
* Default Value

Default values can be seen in the configuration file parser, they are the right-most values per row:

.. literalinclude:: /../oidc_client/config/__init__.py
   :language: python
   :lines: 17-49

The default values can be overwritten and saved to file in the ``config.ini`` configuration file.
The configuration file has three basic sections: ``app`` for application configuration, ``cookie`` for cookie
settings and ``aai`` for oidc client configuration. In addition, a fourth extra section for ELIXIR use case is
provided as ``elixir``. Custom sections can be added freely following the same manner.

.. _app-conf:

Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: /../oidc_client/config/config.ini
   :language: python
   :lines: 17-33

.. _cookie-conf:

Cookie Settings
~~~~~~~~~~~~~~~

.. literalinclude:: /../oidc_client/config/config.ini
   :language: python
   :lines: 35-52

.. _aai-conf:

AAI Server Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: /../oidc_client/config/config.ini
   :language: python
   :lines: 54-89

.. _env:

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The values in the configuration file can be overwritten with environment variables using the exact same name
in all capital letters. For example:

To overwrite the web application port from ``8080`` to ``3000``, one set the following environment variable:

.. code-block:: console

    export PORT=3000

.. note:: Environment variables ``HOST`` and ``PORT`` are used when running the web application with aiohttp.
          When running the web application in production server using gunicorn, environment variables
          ``APP_HOST`` and ``APP_PORT`` are used instead. More on this topic in the Setup Instructions.
