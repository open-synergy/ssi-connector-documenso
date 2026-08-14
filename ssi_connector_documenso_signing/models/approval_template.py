# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ApprovalTemplate(models.Model):
    """Add an optional Documenso signing template to approval templates.

    When ``documenso_signing_template_id`` is set, the approval flow for
    documents using this template is driven by a Documenso signature
    request instead of the standard approval-record flow.
    """

    _name = "approval.template"
    _inherit = "approval.template"

    documenso_signing_template_id = fields.Many2one(
        comodel_name="documenso.signing.template",
        string="Documenso Signing Template",
        ondelete="set null",
        help="When set, the approval process will be replaced by a Documenso "
        "signature request created from this template. Approval is considered "
        "complete when all signature requests are in 'signed' state.",
    )
