# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumensoSigningTemplateSigner(models.Model):
    _name = "documenso.signing.template.signer"
    _description = "Documenso Signing Template Signer"
    _order = "signing_order, id"

    template_id = fields.Many2one(
        comodel_name="documenso.signing.template",
        string="Template",
        required=True,
        ondelete="cascade",
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
        "to position the signature field. E.g. {{SIGN_1}}, {{SIGN_DIRECTOR}}.",
    )
    signature_width = fields.Float(
        string="Signature Width (%)",
        help="Custom width of the signature field as a percentage of the page width (0–100). "
        "Leave at 0 to use the default minimum of 15%.",
    )
    signature_height = fields.Float(
        string="Signature Height (%)",
        help="Custom height of the signature field as a percentage of the page height (0–100). "
        "Leave at 0 to use the default minimum of 3%.",
    )
    partner_code = fields.Text(
        string="Partner Python Code",
        required=True,
        help="Python expression that resolves to the res.partner for this signer.\n"
        "Available variables:\n"
        "  - document : the source record (env[res_model].browse(res_id) of the "
        "signature request)\n"
        "  - env      : Odoo Environment\n"
        "  - time, datetime, dateutil, timezone, float_compare, "
        "b64encode, b64decode\n\n"
        "Examples:\n"
        "  document.partner_id\n"
        "  document.employee_id.user_id.partner_id\n"
        "  env.ref('base.res_partner_1')\n"
        "  env['res.partner'].browse(42)",
    )
