# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Webhook Controller
==============================

Provides an HTTP endpoint that Documenso can call to notify Odoo about
signing events (e.g. document completed, signer signed, etc.).

Configure the webhook URL in Documenso settings as::

    https://your-odoo-instance.com/documenso/webhook

The endpoint accepts JSON POST requests and delegates to
``documenso.signature.request.process_webhook()``.
"""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DocumensoWebhookController(http.Controller):
    @http.route(
        "/documenso/webhook",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def documenso_webhook(self, **kwargs):
        """Handle incoming webhook from Documenso.

        The request body should be a JSON object with at least:
          - ``event``:  event type string
          - ``data``:   dict with document / recipient information

        Returns a simple acknowledgement dict.
        """
        try:
            payload = json.loads(request.httprequest.data)
        except (json.JSONDecodeError, TypeError):
            payload = kwargs

        _logger.info(
            "Received Documenso webhook: event=%s",
            payload.get("event", "unknown"),
        )

        # Use sudo because webhooks arrive without user authentication
        request.env["documenso.signature.request"].sudo().process_webhook(payload)

        return {"status": "ok"}
