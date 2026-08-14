# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class DocumensoSignatureRequestApproval(models.Model):
    """Extend ``documenso.signature.request`` to notify linked documents that
    use ``mixin.documenso_signing_approval`` when the request state changes to
    'signed' (triggers approval) or 'cancelled' (triggers rejection).
    """

    _inherit = "documenso.signature.request"

    def write(self, vals):
        """Notify linked approval documents on signed/cancelled transitions.

        :param vals: values passed to the standard ``write()``
        :return: the result of the overridden ``write()``
        """
        result = super().write(vals)
        new_state = vals.get("state")
        if new_state in ("signed", "cancelled"):
            self._notify_documenso_approval_documents(new_state)
        return result

    def _notify_documenso_approval_documents(self, new_state):
        """For each request, check if the linked document uses
        ``mixin.documenso_signing_approval`` AND this specific request is the
        designated ``approval_signature_request_id``. If so, trigger the
        corresponding approval callback.
        """
        for rec in self:
            if not rec.res_model or not rec.res_id:
                continue
            if rec.res_model not in self.env:
                continue
            DocModel = self.env[rec.res_model]
            # Only handle models that expose the approval_signature_request_id field
            if "approval_signature_request_id" not in DocModel._fields:
                continue
            document = DocModel.sudo().browse(rec.res_id).exists()
            if not document:
                continue
            if document.approval_signature_request_id.id != rec.id:
                continue
            if new_state == "signed":
                document._on_documenso_approval_signed()
            elif new_state == "cancelled":
                # Guard against acting on documents already in a final state
                final_states = (
                    document._approval_reject_state,
                    document._approval_cancel_state,
                )
                if document[document._approval_state_field] not in final_states:
                    document._on_documenso_approval_cancelled()
