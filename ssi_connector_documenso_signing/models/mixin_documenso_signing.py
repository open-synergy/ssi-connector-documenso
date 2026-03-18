# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class MixinDocumensoSigning(models.AbstractModel):
    _name = "mixin.documenso_signing"
    _inherit = [
        "mixin.decorator",
    ]
    _description = "Mixin Object for Documenso Signing"

    _documenso_signing_create_page = False
    _documenso_signing_page_xpath = "//page[last()]"

    signature_request_ids = fields.One2many(
        string="Signature Requests",
        comodel_name="documenso.signature.request",
        inverse_name="res_id",
        domain=lambda self: [("res_model", "=", self._name)],
        auto_join=True,
    )
    signature_request_count = fields.Integer(
        string="Num. of Signature Requests",
        compute="_compute_signature_request_count",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "signature_request_ids",
    )
    def _compute_signature_request_count(self):
        for record in self:
            criteria = [
                ("res_model", "=", self._name),
                ("res_id", "=", record.id),
            ]
            record.signature_request_count = self.env[
                "documenso.signature.request"
            ].search_count(criteria)

    @ssi_decorator.insert_on_form_view()
    def _documenso_signing_insert_form_element(self, view_arch):
        if self._documenso_signing_create_page:
            view_arch = self._add_view_element(
                view_arch=view_arch,
                qweb_template_xml_id="ssi_connector_documenso_signing.documenso_signing_page",
                xpath=self._documenso_signing_page_xpath,
                position="after",
            )
        return view_arch

    def action_open_signature_requests(self):
        self.ensure_one()
        return {
            "name": _("Signature Requests"),
            "type": "ir.actions.act_window",
            "res_model": "documenso.signature.request",
            "view_mode": "tree,form",
            "domain": [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }
