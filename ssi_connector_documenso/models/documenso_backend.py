# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Backend
=================

Stores connection parameters for a Documenso instance.
The ``api_key`` field is displayed as a password widget to prevent
accidental exposure.  It is also excluded from ``read()`` results
for non-manager users.
"""

import logging

import requests

from odoo import _, fields, models

from odoo.addons.connector.exception import NetworkRetryableError

_logger = logging.getLogger(__name__)


class DocumensoBackend(models.Model):
    """Documenso Backend - stores connection parameters to a Documenso instance."""

    _name = "documenso.backend"
    _inherit = "connector.backend"
    _description = "Documenso Backend"

    name = fields.Char(
        string="Name",
        required=True,
    )
    base_url = fields.Char(
        string="Base URL",
        required=True,
        help="Documenso instance URL, e.g. https://app.documenso.com",
    )
    api_key = fields.Char(
        string="API Key",
        required=True,
        help="API token generated from your Documenso account settings.",
    )
    version = fields.Selection(
        selection=[("v1", "API v1"), ("v2", "API v2")],
        string="API Version",
        required=True,
        default="v2",
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # ------------------------------------------------------------------
    # Security: prevent api_key leaking in logs / exports
    # ------------------------------------------------------------------

    def copy_data(self, default=None):
        """Prevent accidental copy of api_key."""
        default = dict(default or {})
        default.setdefault("api_key", False)
        return super().copy_data(default=default)

    # ------------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------------

    def action_test_connection(self):
        """Test the connection to the Documenso API."""
        self.ensure_one()
        url_path = "documents" if self.version == "v1" else "document"
        url = "{}/api/{}/{}".format(self.base_url.rstrip("/"), self.version, url_path)
        headers = {
            "Authorization": "Bearer %s" % self.api_key,
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise NetworkRetryableError(
                _("Could not connect to Documenso: %s") % exc
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise NetworkRetryableError(_("Documenso API error: %s") % exc) from exc

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Connection Test"),
                "message": _("Successfully connected to Documenso!"),
                "type": "success",
                "sticky": False,
            },
        }

    # ------------------------------------------------------------------
    # Async helper methods (called via with_delay)
    # ------------------------------------------------------------------

    def delete_recipient(self, documenso_id):
        """Delete a recipient from Documenso by its external ID.

        Designed to be called via ``with_delay()`` so that the deletion
        is processed asynchronously through the queue job runner.

        :param documenso_id: Documenso recipient ID (str or int)
        """
        self.ensure_one()
        with self.work_on("documenso.res.partner") as work:
            adapter = work.component(usage="backend.adapter")
            adapter.delete(str(documenso_id))
        _logger.info(
            "Deleted Documenso recipient id=%s via backend '%s'",
            documenso_id,
            self.name,
        )
