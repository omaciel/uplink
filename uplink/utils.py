# coding=utf-8
"""Utility functions for Satellite tests."""
import uuid

import requests


# A mapping between URLs and SHA 256 checksums. Used by get_sha256_checksum().
_CHECKSUM_CACHE = {}


def uuid4():
    """Return a random UUID, as a unicode string."""
    return type('')(uuid.uuid4())


def http_get(url, **kwargs):
    """Issue a HTTP request to the ``url`` and return the response content.

    This is useful for downloading file contents over HTTP[S].

    :param url: the URL where the content should be get.
    :param kwargs: additional kwargs to be passed to ``requests.get``.
    :returns: the response content of a GET request to ``url``.
    """
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response.content
