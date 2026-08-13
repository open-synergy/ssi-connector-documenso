# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Backend Adapter
=========================

Base adapter that wraps HTTP calls to the Documenso REST API.
Concrete adapters for specific resources (recipients, documents, …) will
inherit from :class:`DocumensoBaseAdapter`.

Authentication is handled via a Bearer token in the ``Authorization``
header.  The ``api_key`` is read from the backend record and is never
written to logs.
"""

import logging

import requests

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import NetworkRetryableError

_logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds


class DocumensoBaseAdapter(AbstractComponent):
    """Base Documenso Adapter: holds helpers for HTTP calls."""

    _name = "documenso.backend.adapter"
    _inherit = "base.backend.adapter.crud"
    _collection = "documenso.backend"

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @property
    def _base_url(self):
        """Return the versioned base URL of the Documenso API.

        Built from the backend record's ``base_url`` and ``version``,
        e.g. ``https://app.documenso.com/api/v1``.

        :return: base URL string, without a trailing slash
        """
        backend = self.backend_record
        return "{}/api/{}".format(
            backend.base_url.rstrip("/"),
            backend.version,
        )

    @property
    def _headers(self):
        """Return the default HTTP headers for Documenso API calls.

        Includes the ``Authorization`` bearer token built from the
        backend record's ``api_key`` and a JSON ``Content-Type``.

        :return: dict of HTTP header name/value pairs
        """
        return {
            "Authorization": "Bearer %s" % self.backend_record.api_key,
            "Content-Type": "application/json",
        }

    @property
    def _auth_headers(self):
        """Headers with only authentication (no Content-Type).

        Used for multipart/form-data uploads where Content-Type
        must be set automatically by the requests library.
        """
        return {
            "Authorization": "Bearer %s" % self.backend_record.api_key,
        }

    def _request(self, method, path, raw=False, **kwargs):
        """Make an HTTP request to the Documenso API.

        :param method: HTTP method (get, post, put, patch, delete)
        :param path:   API path relative to the base URL
        :param raw:    If True, return raw response bytes instead of JSON.
                       Useful for binary endpoints like PDF downloads.
        :raises NetworkRetryableError: on connection / timeout errors
        """
        url = "{}/{}".format(self._base_url, path.lstrip("/"))
        kwargs.setdefault("timeout", _DEFAULT_TIMEOUT)
        kwargs.setdefault("headers", self._headers)

        try:
            response = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise NetworkRetryableError(
                "A network error occurred while trying to communicate with "
                "Documenso: %s" % exc
            ) from exc

        if not response.ok:
            try:
                body = response.json()
            except Exception:
                body = response.text
            raise requests.exceptions.HTTPError(
                "{} {} for url: {}\nResponse body: {}".format(
                    response.status_code,
                    response.reason,
                    response.url,
                    body,
                ),
                response=response,
            )
        if raw:
            return response.content
        if response.content:
            return response.json()
        return {}

    def test_connection(self):
        """Simple connectivity test: fetch documents list.

        Uses v1 (``documents``) or v2 (``document``) endpoint path
        depending on the configured backend version.
        """
        version = self.backend_record.version
        path = "documents" if version == "v1" else "document"
        return self._request("get", path)

    # ------------------------------------------------------------------ #
    #  CRUDAdapter stubs (override in sub-classes)                        #
    # ------------------------------------------------------------------ #

    def search(self, *args, **kwargs):
        """Search for external ids matching the given criteria.

        Abstract stub: concrete adapters must override this to call
        the relevant Documenso list endpoint (recipients, documents,
        …) and return the matching external ids.

        :raises NotImplementedError: always, in this base adapter
        """
        raise NotImplementedError

    def read(self, external_id, *args, **kwargs):
        """Read a single record from the Documenso API.

        Abstract stub: concrete adapters must override this to call
        the relevant Documenso "get" endpoint for ``external_id`` and
        return the record data.

        :param external_id: id of the record on the Documenso side
        :raises NotImplementedError: always, in this base adapter
        """
        super().read(external_id, *args, **kwargs)
        raise NotImplementedError

    def search_read(self, *args, **kwargs):
        """Search and read matching records from the Documenso API.

        Abstract stub: concrete adapters must override this to call
        the relevant Documenso list endpoint and return the matching
        records' data.

        :raises NotImplementedError: always, in this base adapter
        """
        raise NotImplementedError

    def create(self, data):
        """Create a new record on the Documenso API.

        Abstract stub: concrete adapters must override this to call
        the relevant Documenso "create" endpoint with ``data`` and
        return the created record's data.

        :param data: dict of values to send to the Documenso API
        :raises NotImplementedError: always, in this base adapter
        """
        super().create(data)
        raise NotImplementedError

    def write(self, external_id, data):
        """Update an existing record on the Documenso API.

        Abstract stub: concrete adapters must override this to call
        the relevant Documenso "update" endpoint for ``external_id``
        with ``data``.

        :param external_id: id of the record on the Documenso side
        :param data: dict of values to send to the Documenso API
        :raises NotImplementedError: always, in this base adapter
        """
        super().write(external_id, data)
        raise NotImplementedError

    def delete(self, external_id):
        """Delete a record on the Documenso API.

        Abstract stub: concrete adapters must override this to call
        the relevant Documenso "delete" endpoint for ``external_id``.

        :param external_id: id of the record on the Documenso side
        :raises NotImplementedError: always, in this base adapter
        """
        raise NotImplementedError
