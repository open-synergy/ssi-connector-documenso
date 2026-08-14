# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Document/Signing Adapter
====================================

Implements operations against the Documenso v2 REST API for
the signing workflow.

Key endpoints (v2):

  POST   /api/v2/document/create                   – create document (multipart)
  GET    /api/v2/document/{id}                      – get document details
  POST   /api/v2/document/recipient/create-many     – add signers (batch)
  POST   /api/v2/document/distribute                – send for signing
  GET    /api/v2/document/{id}/download              – download signed copy
"""

import json
import logging

import requests

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class DocumensoSigningAdapter(Component):
    """Adapter for Documenso document / signing operations (v2 API)."""

    _name = "documenso.signature.request.adapter"
    _inherit = "documenso.backend.adapter"
    _apply_on = ["documenso.signature.request"]
    _usage = "backend.adapter"

    @property
    def _base_url(self):
        """Override to always use the v2 API for document operations.

        The v2 API supports direct file upload via multipart/form-data,
        while v1 requires S3 transport for presigned URL uploads.
        """
        backend = self.backend_record
        return "{}/api/v2".format(backend.base_url.rstrip("/"))

    # ------------------------------------------------------------------ #
    #  Document operations                                                #
    # ------------------------------------------------------------------ #

    def create_document(self, title, pdf_content, recipients=None):
        """Create a document on Documenso and upload the PDF.

        Uses the Documenso v2 ``POST /document/create`` endpoint which
        accepts ``multipart/form-data`` with:

        * ``payload`` – JSON string with ``title``, ``recipients``, etc.
        * ``file``    – the raw PDF binary.

        This avoids the v1 presigned-URL flow which requires S3 transport
        to be configured on the server.

        :param title:       Document title / filename
        :param pdf_content: raw PDF bytes
        :param recipients:  list of dicts with keys ``name``, ``email``,
                            ``role`` and optionally ``signingOrder``.
        :returns: dict with document metadata including ``id``
        """
        payload = {
            "title": title,
        }
        if recipients:
            payload["recipients"] = recipients

        doc_result = self._request(
            "post",
            "document/create",
            headers=self._auth_headers,
            data={"payload": json.dumps(payload)},
            files={"file": (title, pdf_content, "application/pdf")},
        )
        return doc_result

    def get_document(self, document_id):
        """Fetch document details from Documenso.

        :param document_id: Documenso document ID
        :returns: dict with document details including status and recipients
        """
        return self._request("get", "document/{}".format(document_id))

    def add_signers(self, document_id, signers):
        """Add recipients/signers to a document in batch.

        Uses the v2 ``POST /document/recipient/create-many`` endpoint
        which accepts multiple recipients in a single call.

        :param document_id: Documenso document ID
        :param signers: list of dicts, each with keys:
            - ``name``: signer display name
            - ``email``: signer email
            - ``role``: SIGNER / CC / APPROVER / VIEWER / ASSISTANT
            - ``signingOrder``: (optional) integer ordering
        :returns: API response dict with ``recipients`` list
        """
        return self._request(
            "post",
            "document/recipient/create-many",
            json={
                "documentId": int(document_id),
                "recipients": signers,
            },
        )

    def create_fields(self, document_id, fields_data):
        """Create signature/form fields on a document.

        Uses the v2 ``POST /document/field/create-many`` endpoint.
        Each signer recipient **must** have at least one field before
        the document can be distributed.

        :param document_id: Documenso document ID
        :param fields_data: list of field dicts, each with:
            - ``recipientId``: Documenso recipient ID (int)
            - ``type``: field type, e.g. ``SIGNATURE``, ``FREE_SIGNATURE``
            - ``pageNumber``: 1-based page number
            - ``pageX``: X position as percentage (0-100)
            - ``pageY``: Y position as percentage (0-100)
            - ``width``: width as percentage (0-100)
            - ``height``: height as percentage (0-100)
        :returns: API response dict with ``fields`` list
        """
        return self._request(
            "post",
            "document/field/create-many",
            json={
                "documentId": int(document_id),
                "fields": fields_data,
            },
        )

    def send_document(self, document_id):
        """Distribute the document for signing (DRAFT → PENDING).

        Uses the v2 ``POST /document/distribute`` endpoint.

        :param document_id: Documenso document ID
        :returns: API response dict
        """
        return self._request(
            "post",
            "document/distribute",
            json={"documentId": int(document_id)},
        )

    def download_signed_document(self, document_id):
        """Download the completed/signed PDF.

        The v2 ``GET /document/{id}/download`` endpoint returns the raw
        PDF bytes directly (Content-Type: application/pdf).

        :param document_id: Documenso document ID
        :returns: raw PDF bytes or None if not available
        """
        try:
            return self._request(
                "get",
                "document/{}/download".format(document_id),
                raw=True,
            )
        except Exception as exc:
            _logger.warning(
                "Error downloading signed PDF for doc %s: %s",
                document_id,
                exc,
            )
            return None

    # ------------------------------------------------------------------ #
    #  CRUDAdapter stubs (not directly used for signing, but required)    #
    # ------------------------------------------------------------------ #

    def search(self, *args, **kwargs):
        """Return the raw list of documents known to Documenso.

        Present only to satisfy the ``CRUDAdapter`` interface; unlike a
        real search it ignores ``args``/``kwargs`` and always proxies to
        ``GET /document``.

        :returns: API response dict with the document list
        """
        return self._request("get", "document")

    def read(self, external_id, *args, **kwargs):
        """Delegate to ``get_document`` after the parent no-op call.

        :param external_id: Documenso document ID
        :returns: dict with document details (see ``get_document``)
        """
        super().read(external_id, *args, **kwargs)
        return self.get_document(external_id)

    def create(self, data):
        """Reject direct creation through the generic CRUD interface.

        :param data: unused
        :raises NotImplementedError: always — use ``create_document()``
            instead so the multipart PDF upload flow is followed
        """
        super().create(data)
        raise NotImplementedError("Use create_document() for signing workflow.")

    def write(self, external_id, data):
        """Reject direct writes through the generic CRUD interface.

        :param external_id: unused
        :param data: unused
        :raises NotImplementedError: always — use the dedicated methods
            (``add_signers``, ``create_fields``, ``send_document``, …)
            instead
        """
        super().write(external_id, data)
        raise NotImplementedError("Use specific methods for document operations.")

    def delete(self, external_id):
        """Delete/cancel a document on Documenso."""
        try:
            self._request(
                "post",
                "document/delete",
                json={"documentId": int(external_id)},
            )
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return True
            raise
        return True
