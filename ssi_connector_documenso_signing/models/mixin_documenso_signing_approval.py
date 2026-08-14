# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class MixinDocumensoSigningApproval(models.AbstractModel):
    """Mixin combining Documenso Signing with Multiple Approval.

    When an ``approval.template`` has a ``documenso_signing_template_id`` set,
    the normal approval-record flow is replaced by a single
    ``documenso.signature.request`` stored in ``approval_signature_request_id``.
    The document is considered approved once that request reaches 'signed' state,
    and rejected if the request is cancelled (e.g. a signer declines in Documenso).
    """

    _name = "mixin.documenso_signing_approval"
    _inherit = [
        "mixin.documenso_signing",
        "mixin.multiple_approval",
    ]
    _description = "Mixin Object for Documenso Signing Approval"

    approval_signature_request_id = fields.Many2one(
        comodel_name="documenso.signature.request",
        string="Approval Signature Request",
        copy=False,
        ondelete="set null",
        help="The specific signature request used to determine approval status. "
        "Set automatically when the approval template uses a Documenso signing "
        "template. Other signature requests on this document are not affected.",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _use_documenso_approval(self):
        """Return True if the active approval template uses Documenso signing."""
        self.ensure_one()
        return bool(
            self.approval_template_id
            and self.approval_template_id.documenso_signing_template_id
        )

    # ------------------------------------------------------------------
    # Override: form view insertion — use the approval-aware page template
    # ------------------------------------------------------------------

    @ssi_decorator.insert_on_form_view()
    def _documenso_signing_insert_form_element(self, view_arch):
        """Insert the approval-aware "Documenso Signing" page.

        Overrides the base mixin's hook to use the approval-specific
        QWeb template (``documenso_signing_approval_page``) instead of
        the plain one, so approval-related information is shown too.

        :param view_arch: current view architecture (``etree`` element)
        :return: the (possibly modified) view architecture
        """
        if self._documenso_signing_create_page:
            xml_id = (
                "ssi_connector_documenso_signing" ".documenso_signing_approval_page"
            )
            view_arch = self._add_view_element(
                view_arch=view_arch,
                qweb_template_xml_id=xml_id,
                xpath=self._documenso_signing_page_xpath,
                position="after",
            )
        return view_arch

    # ------------------------------------------------------------------
    # Override: approved / rejected computation
    # ------------------------------------------------------------------

    def _compute_approved_rejected(self):
        """Derive ``approved``/``rejected`` from the Documenso request.

        When Documenso-based approval is active, ``approved`` mirrors
        ``approval_signature_request_id.state == 'signed'`` and
        ``rejected`` mirrors the record already being in the rejection
        state. Otherwise, falls back to the standard computation.
        """
        for rec in self:
            if rec._use_documenso_approval() and rec.approval_signature_request_id:
                rec.approved = rec.approval_signature_request_id.state == "signed"
                rec.rejected = rec.state == rec._approval_reject_state
            else:
                super(MixinDocumensoSigningApproval, rec)._compute_approved_rejected()

    # ------------------------------------------------------------------
    # Override: approval record creation → signature request creation
    # ------------------------------------------------------------------

    def create_approver(self):
        """When the template has a Documenso signing template, create a single
        ``documenso.signature.request`` instead of standard approval records.
        The reference is stored in ``approval_signature_request_id``.
        Returns an empty ``approval.approval`` recordset so the caller
        (``set_active``) handles the absence of records gracefully.
        """
        self.ensure_one()
        if self._use_documenso_approval():
            request = self._create_documenso_approval_request()
            if request:
                self.sudo().approval_signature_request_id = request.id
            return self.env["approval.approval"]
        return super().create_approver()

    def _create_documenso_approval_request(self):
        """Create a ``documenso.signature.request`` based on the signing template
        linked to the active approval template.
        """
        self.ensure_one()
        signing_template = self.approval_template_id.documenso_signing_template_id
        backend = self.env["documenso.backend"].search([("active", "=", True)], limit=1)
        vals = {
            "signing_template_id": signing_template.id,
            "res_model": self._name,
            "res_id": self.id,
            "py3o_report_id": signing_template.py3o_report_id.id,
        }
        if backend:
            vals["backend_id"] = backend.id
        request = self.env["documenso.signature.request"].create(vals)
        if signing_template.signer_template_ids:
            request._apply_template_signers()
        return request

    # ------------------------------------------------------------------
    # Callbacks invoked by signature request state changes
    # ------------------------------------------------------------------

    def _on_documenso_approval_signed(self):
        """Called when ``approval_signature_request_id`` reaches 'signed' state.
        Triggers the post-approval flow (equivalent to all approvers having approved).
        """
        self.ensure_one()
        rec = self.sudo().with_context(bypass_policy_check=True)
        rec._run_pre_approve_action()
        if rec._after_approved_method:
            getattr(rec, rec._after_approved_method)()
        rec._run_post_approve_action()
        self._notify_approve_action()

    def _on_documenso_approval_cancelled(self):
        """Called when ``approval_signature_request_id`` is cancelled
        (e.g. a signer declines in Documenso). Transitions the document to
        the rejection state without requiring manual intervention.
        """
        self.ensure_one()
        self.sudo().write({self._approval_state_field: self._approval_reject_state})
        self._notify_reject_action()

    # ------------------------------------------------------------------
    # Override: write — clear approval request when resetting to initial state
    # ------------------------------------------------------------------

    def write(self, vals):
        """Cancel the linked signature request when reset to the from-state.

        When ``vals`` moves the record back to ``_approval_from_state``,
        any pending/sent ``approval_signature_request_id`` is cancelled
        and the reference is cleared in the same call.

        :param vals: values passed to the standard ``write()``
        :return: the result of the overridden ``write()``
        """
        if vals.get(self._approval_state_field) == self._approval_from_state:
            # Cancel the linked signature request before it is dereferenced.
            for rec in self:
                if (
                    rec.approval_signature_request_id
                    and rec.approval_signature_request_id.state in ("draft", "sent")
                ):
                    rec.approval_signature_request_id.write({"state": "cancelled"})
            # Clear the reference within the same write call to avoid a
            # second ORM round-trip and to keep the parent's cleanup consistent.
            vals = dict(vals, approval_signature_request_id=False)
        return super().write(vals)

    # ------------------------------------------------------------------
    # Override: unlink — cancel pending approval requests on deletion
    # ------------------------------------------------------------------

    def unlink(self):
        """Cancel pending signature requests before deleting the record.

        :return: the result of the overridden ``unlink()``
        """
        for rec in self:
            if (
                rec.approval_signature_request_id
                and rec.approval_signature_request_id.state in ("draft", "sent")
            ):
                rec.approval_signature_request_id.write({"state": "cancelled"})
        return super().unlink()

    # ------------------------------------------------------------------
    # Notification helpers (re-use parent messages)
    # ------------------------------------------------------------------

    def _prepare_approve_action_notification(self):
        """Build the message announcing a Documenso-driven approval.

        :return: translated notification string
        """
        self.ensure_one()
        msg = _("%s %s approved via Documenso signing") % (
            self._description,
            self.display_name,
        )
        return msg

    def _prepare_reject_action_notification(self):
        """Build the message announcing a Documenso-driven rejection.

        :return: translated notification string
        """
        self.ensure_one()
        msg = _("%s %s rejected — Documenso signing was cancelled") % (
            self._description,
            self.display_name,
        )
        return msg
