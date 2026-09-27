#!/bin/bash

set -e

if [[ "${WAIT_FOR_DB:-}" = true || "${WAIT_FOR_DB:-}" = True ]]; then
    dockerize -wait "tcp://${DB_HOST}:${DB_PORT}" -timeout 300s
fi

exec "$@"
