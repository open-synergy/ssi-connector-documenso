# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DocumensoSigningTemplate(models.Model):
    _name = "documenso.signing.template"
    _description = "Documenso Signing Template"
    _inherit = ["mixin.localdict"]

    name = fields.Char(
        string="Name",
        required=True,
    )
    res_model = fields.Char(
        string="Source Model",
        required=True,
        help="Technical name of the Odoo model this template applies to "
        "(e.g. sale.order, account.move).",
    )
    allowed_py3o_report_ids = fields.Many2many(
        string="Allowed Py3o Reports",
        comodel_name="ir.actions.report",
        compute="_compute_allowed_py3o_report_ids",
        store=False,
    )
    py3o_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Py3o Report",
        domain="[('id', 'in', allowed_py3o_report_ids)]",
        help="The py3o report action used to generate the PDF document. "
        "Only py3o reports with PDF output are listed.",
    )
    signer_template_ids = fields.One2many(
        comodel_name="documenso.signing.template.signer",
        inverse_name="template_id",
        string="Signer Templates",
        copy=True,
    )
    active = fields.Boolean(
        default=True,
    )

    @api.depends("res_model")
    def _compute_allowed_py3o_report_ids(self):
        Report = self.env["ir.actions.report"]
        for rec in self:
            criteria = [
                ("report_type", "=", "py3o"),
                ("py3o_filetype", "=", "pdf"),
            ]
            if rec.res_model:
                criteria.append(("model", "=", rec.res_model))
            rec.allowed_py3o_report_ids = Report.search(criteria)

    @api.onchange("res_model")
    def _onchange_res_model(self):
        self.py3o_report_id = False
