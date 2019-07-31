#!/bin/bash

THE_HOST=${APP_HOST:="0.0.0.0"}
THE_PORT=${APP_PORT:="8080"}

echo 'Start oidc-client web server'
exec gunicorn oidc_client.app:init --bind $THE_HOST:$THE_PORT --worker-class aiohttp.GunicornUVLoopWebWorker --workers 4