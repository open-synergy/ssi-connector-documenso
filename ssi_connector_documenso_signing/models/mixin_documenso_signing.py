# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models

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
        if not self._documenso_signing_create_page:
            return view_arch
        nodes = view_arch.xpath(self._documenso_signing_page_xpath)
        if not nodes:
            return view_arch
        page_element = etree.fromstring(
            '<page name="page_documenso_signing" string="Signature Requests">'
            '<field name="signature_request_ids" nolabel="1"/>'
            "</page>"
        )
        page_element.find("field").set("options", "{'always_reload': True}")
        nodes[0].addnext(page_element)
        return view_arch
