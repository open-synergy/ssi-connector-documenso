# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Signature Signer
============================

Model representing an individual signer within a signature request.
Each signer links to a ``res.partner`` and stores:

* ``role`` – the Documenso role (SIGNER, CC, APPROVER, VIEWER)
* ``signing_order`` – sequence order for ordered signing workflows
* ``signature_anchor`` – text placeholder that Documenso uses to position
  the signature field in the PDF (e.g. ``{{SIGN_<partner_id>}}``)
* ``signing_status`` – individual tracking (PENDING, SIGNED, DECLINED, …)
"""

from odoo import api, fields, models


class DocumensoSignatureSigner(models.Model):
    _name = "documenso.signature.signer"
    _description = "Documenso Signature Signer"
    _order = "signing_order, id"
    _rec_name = "partner_id"

    request_id = fields.Many2one(
        comodel_name="documenso.signature.request",
        string="Signature Request",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Signer",
        required=True,
        ondelete="restrict",
        help="Contact who will sign the document.",
    )
    partner_email = fields.Char(
        related="partner_id.email",
        string="Email",
        readonly=True,
    )
    role = fields.Selection(
        selection=[
            ("SIGNER", "Signer"),
            ("CC", "CC (Copy)"),
            ("APPROVER", "Approver"),
            ("VIEWER", "Viewer"),
        ],
        string="Role",
        default="SIGNER",
        required=True,
        help="The role this contact plays in the signing process.",
    )
    signing_order = fields.Integer(
        string="Signing Order",
        default=1,
        help="Order in which this signer should sign. "
        "Lower numbers sign first. Use the same number for parallel signing.",
    )
    signature_anchor = fields.Char(
        string="Signature Anchor",
        help="Text placeholder in the py3o template that Documenso will use "
        "to position the signature field. "
        "E.g. {{SIGN_1}}, {{SIGN_DIRECTOR}}, {{SIGN_<partner_id>}}. "
        "Must be unique per signer within the same document.",
    )
    signing_status = fields.Selection(
        selection=[
            ("PENDING", "Pending"),
            ("SENT", "Sent"),
            ("OPENED", "Opened"),
            ("SIGNED", "Signed"),
            ("DECLINED", "Declined"),
            ("CANCELLED", "Cancelled"),
        ],
        string="Signing Status",
        default="PENDING",
        readonly=True,
        tracking=True,
    )
    documenso_recipient_id = fields.Char(
        string="Documenso Recipient ID",
        readonly=True,
        help="External ID of this recipient on Documenso.",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """Auto-suggest a signature anchor based on the partner."""
        if self.partner_id and not self.signature_anchor:
            self.signature_anchor = "{{{{SIGN_{}}}}}".format(self.partner_id.id)
