# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class DocumensoCreateSigningWizard(models.TransientModel):
    _name = "documenso.create.signing.wizard"
    _description = "Create Documenso Signature Request Wizard"

    res_model = fields.Char(
        string="Source Model",
        required=True,
        readonly=True,
    )
    res_id = fields.Integer(
        string="Source Record ID",
        required=True,
        readonly=True,
    )
    signing_template_id = fields.Many2one(
        comodel_name="documenso.signing.template",
        string="Signing Template",
        required=True,
        domain="[('res_model', '=', res_model)]",
    )
    backend_id = fields.Many2one(
        comodel_name="documenso.backend",
        string="Documenso Backend",
        required=True,
        default=lambda self: self.env["documenso.backend"].search(
            [("active", "=", True)], limit=1
        ),
    )

    def action_confirm(self):
        self.ensure_one()
        template = self.signing_template_id
        request = self.env["documenso.signature.request"].create(
            {
                "signing_template_id": template.id,
                "res_model": template.res_model,
                "res_id": self.res_id,
                "backend_id": self.backend_id.id,
                "py3o_report_id": template.py3o_report_id.id
                if template.py3o_report_id
                else False,
            }
        )
        request._apply_template_signers()
        return {
            "type": "ir.actions.act_window",
            "name": _("Signature Request"),
            "res_model": "documenso.signature.request",
            "res_id": request.id,
            "view_mode": "form",
            "target": "current",
        }
