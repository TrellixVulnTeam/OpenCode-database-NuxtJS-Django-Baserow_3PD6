from .base import *  # noqa: F403, F401
import os
import ssl

if REDIS_PROTOCOL == "rediss" or "rediss" in REDIS_URL:  # noqa: F405
    # We need to set the certificate check to None, otherwise it is not compatible with
    # the `heroku-redis:hobby-dev` addon. The URL generated by that addon is over a
    # secured connection with a self signed certificate. The redis broker could fail
    # if the certificate can't be verified.
    CELERY_REDBEAT_REDIS_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}
    ssl_context = ssl.SSLContext()
    ssl_context.verify_mode = ssl.CERT_NONE
    CHANNELS_REDIS_HOST = {"address": REDIS_URL, "ssl": ssl_context}  # noqa: F405
    CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [CHANNELS_REDIS_HOST]  # noqa: F405

    # The built in healthcheck does not handle customizing ssl_cert_reqs...
    INSTALLED_APPS.remove("health_check.contrib.redis")  # noqa: F405
    for CACHE in CACHES.values():  # noqa: F405
        CACHE["OPTIONS"]["CONNECTION_POOL_KWARGS"] = {"ssl_cert_reqs": None}

# Set the limit of the connection pool based on the amount of workers that must be
# started with a limit of 10, which is the default value. This is needed because the
# `heroku-redis:hobby-dev` doesn't accept more than 20 connections.
CELERY_BROKER_POOL_LIMIT = min(4 * int(os.getenv("BASEROW_AMOUNT_OF_WORKERS", "1")), 10)
CELERY_REDIS_MAX_CONNECTIONS = min(
    4 * int(os.getenv("BASEROW_AMOUNT_OF_WORKERS", "1")), 10
)
