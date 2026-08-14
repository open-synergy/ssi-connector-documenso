# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class MixinDocumensoSigning(models.AbstractModel):
    """Add Documenso signature request tracking to a document model.

    Inheriting models get a ``signature_request_ids`` one2many keyed on
    ``res_model``/``res_id``, an optional "Documenso Signing" form page,
    and an action/button to open a wizard that creates a new signature
    request for the record.
    """

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
        """Count signature requests whose source points to this record."""
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
        """Insert the "Documenso Signing" page into the form view.

        Runs when the form view is built. Only inserts the page when
        ``_documenso_signing_create_page`` is enabled on the inheriting
        model; otherwise the view is returned unchanged.

        :param view_arch: current view architecture (``etree`` element)
        :return: the (possibly modified) view architecture
        """
        if self._documenso_signing_create_page:
            view_arch = self._add_view_element(
                view_arch=view_arch,
                qweb_template_xml_id="ssi_connector_documenso_signing.documenso_signing_page",
                xpath=self._documenso_signing_page_xpath,
                position="after",
            )
        return view_arch

    def action_open_signature_requests(self):
        """Open the list of signature requests linked to this record.

        :return: an ``ir.actions.act_window`` dict for
            ``documenso.signature.request``, filtered to this record
        """
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

    def action_create_signing_request(self):
        """Open the wizard that starts a new Documenso signature request.

        :return: an ``ir.actions.act_window`` dict opening the
            ``create_documenso_signature_request`` wizard, prefilled
            with this record as its source
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Create Signing Request"),
            "res_model": "create_documenso_signature_request",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }
