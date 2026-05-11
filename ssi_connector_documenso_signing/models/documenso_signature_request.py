# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Signature Request
============================

Transactional model that tracks a signature request sent to Documenso.
Each request:

* references a source Odoo record (polymorphic via ``res_model`` / ``res_id``),
* generates a PDF document using a ``report_py3o`` report action,
* uploads the PDF to Documenso along with the list of signers,
* tracks the overall state (draft → sent → signed / cancelled).

Multi-signer
~~~~~~~~~~~~~
A single request can have **many signers**, each represented by a
``documenso.signature.signer`` record linked via ``signer_ids``.
Every signer maps to a ``res.partner`` and stores its own individual
signing status.
"""

import base64
import logging

import fitz  # PyMuPDF

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class DocumensoSignatureRequest(models.Model):
    _name = "documenso.signature.request"
    _description = "Documenso Signature Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    signing_template_id = fields.Many2one(
        comodel_name="documenso.signing.template",
        string="Signing Template",
        ondelete="set null",
        help="Select a signing template to auto-fill source model, report, and signers.",
    )
    backend_id = fields.Many2one(
        comodel_name="documenso.backend",
        string="Documenso Backend",
        required=True,
        ondelete="restrict",
        tracking=True,
        default=lambda self: self.env["documenso.backend"].search(
            [("active", "=", True)], limit=1
        ),
    )
    res_model = fields.Char(
        string="Source Model",
        required=True,
        help="Technical name of the Odoo model that owns the document "
        "(e.g. sale.order, account.move).",
    )
    res_id = fields.Integer(
        string="Source Record ID",
        required=True,
    )
    res_name = fields.Char(
        string="Source Record",
        compute="_compute_res_name",
        store=True,
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
        required=True,
        domain="[('id', 'in', allowed_py3o_report_ids)]",
        help="The py3o report action used to generate the PDF document. "
        "Only py3o reports with PDF output are listed.",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("signed", "Signed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    documenso_document_id = fields.Char(
        string="Documenso Document ID",
        readonly=True,
        copy=False,
        tracking=True,
    )
    signer_ids = fields.One2many(
        comodel_name="documenso.signature.signer",
        inverse_name="request_id",
        string="Signers",
        copy=True,
    )
    signer_count = fields.Integer(
        string="# Signers",
        compute="_compute_signer_count",
    )
    pdf_file = fields.Binary(
        string="Generated PDF",
        readonly=True,
        attachment=True,
        copy=False,
    )
    pdf_filename = fields.Char(
        string="PDF Filename",
        readonly=True,
        copy=False,
    )
    signed_pdf_file = fields.Binary(
        string="Signed PDF",
        readonly=True,
        attachment=True,
        copy=False,
    )
    signed_pdf_filename = fields.Char(
        string="Signed PDF Filename",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    note = fields.Text(
        string="Notes",
    )

    # ------------------------------------------------------------------
    # Computed
    # ------------------------------------------------------------------

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

    @api.onchange("signing_template_id")
    def _onchange_signing_template_id(self):
        template = self.signing_template_id
        if not template:
            return
        self.res_model = template.res_model
        self.py3o_report_id = template.py3o_report_id
        self._apply_template_signers()

    @api.onchange("res_id")
    def _onchange_res_id(self):
        if self.signing_template_id and self.res_id:
            self._apply_template_signers()

    def _apply_template_signers(self):
        """Populate signer_ids from the signing template.

        Evaluates each signer template's ``partner_code`` against the source
        document (``res_model`` / ``res_id``) using the localdict provided by
        ``mixin.localdict`` (with ``document`` set to the source record).
        Replaces any existing signer lines.
        """
        template = self.signing_template_id
        if not template or not template.signer_template_ids:
            return
        if not self.res_model or not self.res_id:
            return

        try:
            source_record = self.env[self.res_model].browse(self.res_id)
            if not source_record.exists():
                return
        except Exception:
            return

        # Build localdict from mixin, then override 'document' to be the
        # source record (env[res_model].browse(res_id) of this request)
        # so that partner_code expressions like 'document.partner_id' work
        # against the actual source document, not the signing template.
        localdict = template._get_default_localdict()
        localdict["document"] = source_record

        new_signers = [(5, 0, 0)]  # clear existing
        for signer_tmpl in template.signer_template_ids:
            if not signer_tmpl.partner_code:
                continue
            try:
                partner = safe_eval(signer_tmpl.partner_code, localdict)
                if hasattr(partner, "id"):
                    partner_id = partner.id
                else:
                    partner_id = int(partner)
            except Exception as exc:
                _logger.warning(
                    "Failed to evaluate partner_code for signer template %s: %s",
                    signer_tmpl.id,
                    exc,
                )
                continue
            new_signers.append(
                (
                    0,
                    0,
                    {
                        "partner_id": partner_id,
                        "role": signer_tmpl.role,
                        "signing_order": signer_tmpl.signing_order,
                        "signature_anchor": signer_tmpl.signature_anchor,
                        "signature_width": signer_tmpl.signature_width,
                        "signature_height": signer_tmpl.signature_height,
                    },
                )
            )
        self.signer_ids = new_signers

    @api.onchange("res_model")
    def _onchange_res_model(self):
        self.py3o_report_id = False

    @api.depends("res_model", "res_id")
    def _compute_res_name(self):
        for rec in self:
            if rec.res_model and rec.res_id:
                try:
                    source = self.env[rec.res_model].browse(rec.res_id)
                    rec.res_name = source.display_name
                except Exception:
                    rec.res_name = "{},{}".format(rec.res_model, rec.res_id)
            else:
                rec.res_name = False

    @api.depends("signer_ids")
    def _compute_signer_count(self):
        for rec in self:
            rec.signer_count = len(rec.signer_ids)

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {} ({})".format(
                rec.res_name or rec.res_model,
                rec.backend_id.name,
                rec.state,
            )
            result.append((rec.id, name))
        return result

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def action_generate_pdf(self):
        """Generate the PDF from the py3o report and store it on the record."""
        self.ensure_one()
        if not self.py3o_report_id:
            raise UserError(_("Please select a Py3o Report first."))
        if not self.signer_ids:
            raise UserError(_("Please add at least one signer."))

        report = self.py3o_report_id
        source_record = self.env[self.res_model].browse(self.res_id)
        if not source_record.exists():
            raise UserError(
                _("Source record %s (id=%s) no longer exists.")
                % (self.res_model, self.res_id)
            )

        # Generate the PDF content via py3o
        pdf_content, _ext = report._render_py3o(source_record.ids, {})

        filename = report.gen_report_download_filename(source_record.ids, {})
        if not filename.lower().endswith(".pdf"):
            filename = filename.rsplit(".", 1)[0] + ".pdf"

        self.write(
            {
                "pdf_file": base64.b64encode(pdf_content),
                "pdf_filename": filename,
            }
        )
        _logger.info(
            "Generated PDF '%s' for signature request id=%s",
            filename,
            self.id,
        )
        return True

    # ------------------------------------------------------------------
    # PDF anchor helpers (PyMuPDF / fitz)
    # ------------------------------------------------------------------

    def _find_anchor_positions(self, pdf_bytes):
        """Search the PDF for signature anchor placeholders.

        Scans every page for text matching each signer's
        ``signature_anchor`` value (e.g. ``{{SIGN_51}}``) and returns
        positioning data as percentages of the page size — the format
        Documenso expects.

        :param pdf_bytes: raw PDF content (bytes)
        :returns: dict mapping anchor string → list of dicts::

            {
                "{{SIGN_51}}": [{
                    "pageNumber": 1,
                    "pageX": 62.5,   # percentage of page width
                    "pageY": 80.2,   # percentage of page height
                    "width": 15.0,
                    "height": 3.5,
                }],
                ...
            }
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        results = {}  # anchor_text -> [position_dict, ...]

        # Collect all anchors we need to search for, along with their
        # per-signer custom sizes (fallback to defaults when not set).
        _DEFAULT_SIG_W = 15.0
        _DEFAULT_SIG_H = 3.0
        anchor_sizes = {}  # anchor_text -> (min_width_pct, min_height_pct)
        for signer in self.signer_ids:
            if signer.signature_anchor:
                anchor = signer.signature_anchor.strip()
                anchor_sizes[anchor] = (
                    signer.signature_width or _DEFAULT_SIG_W,
                    signer.signature_height or _DEFAULT_SIG_H,
                )

        if not anchor_sizes:
            doc.close()
            return results

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_rect = page.rect  # full page rectangle
            page_w = page_rect.width
            page_h = page_rect.height

            for anchor, (min_w, min_h) in anchor_sizes.items():
                # search_for returns a list of fitz.Rect for each match
                rects = page.search_for(anchor)
                for rect in rects:
                    # Convert from PDF points to percentages (0-100)
                    # fitz origin is top-left, same as Documenso
                    pct_x = (rect.x0 / page_w) * 100.0
                    pct_y = (rect.y0 / page_h) * 100.0
                    pct_w = ((rect.x1 - rect.x0) / page_w) * 100.0
                    pct_h = ((rect.y1 - rect.y0) / page_h) * 100.0

                    # Use per-signer custom size if set, otherwise enforce
                    # the minimum so the field is actually usable for signing.
                    sig_w = max(pct_w, min_w)
                    sig_h = max(pct_h, min_h)

                    results.setdefault(anchor, []).append(
                        {
                            "pageNumber": page_idx + 1,  # 1-based
                            "pageX": round(pct_x, 2),
                            "pageY": round(pct_y, 2),
                            "width": round(sig_w, 2),
                            "height": round(sig_h, 2),
                        }
                    )

        doc.close()
        return results

    def _redact_anchors_from_pdf(self, pdf_bytes):
        """Remove anchor placeholder texts from the PDF.

        Uses PyMuPDF redaction annotations to white-out the placeholder
        strings so they don't appear in the final signed document.

        :param pdf_bytes: raw PDF content (bytes)
        :returns: cleaned PDF content (bytes) with placeholders removed
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        anchors = set()
        for signer in self.signer_ids:
            if signer.signature_anchor:
                anchors.add(signer.signature_anchor.strip())

        if not anchors:
            cleaned = doc.tobytes()
            doc.close()
            return cleaned

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            for anchor in anchors:
                rects = page.search_for(anchor)
                for rect in rects:
                    # Add a redaction annotation (white fill, no text)
                    page.add_redact_annot(rect, fill=(1, 1, 1))
            # Apply all redactions on this page
            page.apply_redactions()

        cleaned = doc.tobytes()
        doc.close()
        return cleaned

    def action_send_to_documenso(self):
        """Generate PDF (if not yet) and queue the send job."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft requests can be sent to Documenso."))
        if not self.signer_ids:
            raise UserError(_("Please add at least one signer."))

        # Auto-generate PDF if not already present
        if not self.pdf_file:
            self.action_generate_pdf()

        self.with_delay().job_send_to_documenso()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Documenso"),
                "message": _("Document queued for sending to Documenso."),
                "type": "info",
                "sticky": False,
            },
        }

    def _build_signers_payload(self):
        """Build the recipients payload list for the Documenso API."""
        signers_payload = []
        for signer in self.signer_ids:
            signer_data = {
                "name": signer.partner_id.name,
                "email": signer.partner_id.email,
                "role": signer.role,
            }
            if signer.signing_order:
                signer_data["signingOrder"] = signer.signing_order
            signers_payload.append(signer_data)
        return signers_payload

    def _prepare_pdf_data(self):
        """Decode PDF, find anchors, redact them, and return cleaned data.

        Returns:
            tuple: (pdf_data, anchor_positions)
        """
        pdf_data = base64.b64decode(self.pdf_file)
        anchor_positions = self._find_anchor_positions(pdf_data)
        _logger.info(
            "Found anchor positions in PDF: %s",
            {k: len(v) for k, v in anchor_positions.items()},
        )
        if anchor_positions:
            pdf_data = self._redact_anchors_from_pdf(pdf_data)
            self.write({"pdf_file": base64.b64encode(pdf_data)})
        return pdf_data, anchor_positions

    def _map_recipients(self, adapter, documenso_doc_id):
        """Fetch document recipients and map emails to Documenso IDs.

        Returns:
            dict: email (lower) -> documenso recipient id
        """
        doc_data = adapter.get_document(documenso_doc_id)
        returned_recipients = doc_data.get("recipients") or []
        _logger.info(
            "Documenso document %s has %d recipients: %s",
            documenso_doc_id,
            len(returned_recipients),
            [{"id": r.get("id"), "email": r.get("email")} for r in returned_recipients],
        )
        recipient_map = {}
        for r in returned_recipients:
            r_email = (r.get("email") or "").lower().strip()
            r_id = r.get("id")
            if r_email and r_id:
                recipient_map[r_email] = int(r_id)
        # Store recipient IDs on signer records
        for signer in self.signer_ids:
            s_email = (signer.partner_id.email or "").lower().strip()
            if s_email in recipient_map:
                signer.write({"documenso_recipient_id": str(recipient_map[s_email])})
        return recipient_map

    def _build_signature_fields(self, recipient_map, anchor_positions):
        """Build signature field definitions for each SIGNER recipient.

        Returns:
            list: field data dicts for the Documenso API
        """
        fields_data = []
        signers_without_anchor = 0
        for signer in self.signer_ids:
            if signer.role != "SIGNER":
                continue
            s_email = (signer.partner_id.email or "").lower().strip()
            recipient_id = recipient_map.get(s_email)
            if not recipient_id:
                _logger.warning(
                    "No Documenso recipient ID found for signer %s (%s)",
                    signer.partner_id.name,
                    signer.partner_id.email,
                )
                continue
            anchor = (signer.signature_anchor or "").strip()
            positions = anchor_positions.get(anchor, []) if anchor else []
            if positions:
                for pos in positions:
                    fields_data.append(
                        {
                            "type": "SIGNATURE",
                            "recipientId": recipient_id,
                            "pageNumber": pos["pageNumber"],
                            "pageX": pos["pageX"],
                            "pageY": pos["pageY"],
                            "width": pos["width"],
                            "height": pos["height"],
                        }
                    )
                _logger.info(
                    "Signer %s (%s): placed %d signature field(s) " "from anchor '%s'",
                    signer.partner_id.name,
                    s_email,
                    len(positions),
                    anchor,
                )
            else:
                if anchor:
                    _logger.warning(
                        "Anchor '%s' for signer %s not found in PDF. "
                        "Using default position.",
                        anchor,
                        signer.partner_id.name,
                    )
                page_y = min(75.0 + (signers_without_anchor * 8.0), 95.0)
                fields_data.append(
                    {
                        "type": "SIGNATURE",
                        "recipientId": recipient_id,
                        "pageNumber": 1,
                        "pageX": 40.0,
                        "pageY": page_y,
                        "width": 20.0,
                        "height": 5.0,
                    }
                )
                signers_without_anchor += 1
        return fields_data

    def job_send_to_documenso(self):
        """Queue job: upload PDF and signers to Documenso.

        This method is meant to be called via ``with_delay()``.

        The Documenso v2 API workflow is:

        1. ``POST /document/create`` with multipart form-data
           (``payload`` JSON + ``file`` PDF) → returns document object.
        2. ``POST /document/field/create-many`` to place signature
           fields for each signer recipient.
        3. ``POST /document/distribute`` with ``{documentId}``
           → triggers signing emails.
        """
        self.ensure_one()
        with self.backend_id.work_on("documenso.signature.request") as work:
            adapter = work.component(usage="backend.adapter")

            signers_payload = self._build_signers_payload()
            pdf_data, anchor_positions = self._prepare_pdf_data()

            # 1) Create document + upload PDF in one multipart call
            doc_result = adapter.create_document(
                title=self.pdf_filename or "document.pdf",
                pdf_content=pdf_data,
                recipients=signers_payload,
            )
            documenso_doc_id = doc_result.get("id") or doc_result.get("documentId")
            if not documenso_doc_id:
                raise UserError(
                    _("Documenso did not return a document ID. Response: %s")
                    % doc_result
                )

            # 2) Map recipients and create signature fields
            recipient_map = self._map_recipients(adapter, documenso_doc_id)
            fields_data = self._build_signature_fields(recipient_map, anchor_positions)
            if fields_data:
                adapter.create_fields(documenso_doc_id, fields_data)

            # 3) Send the document for signing
            adapter.send_document(documenso_doc_id)

            # 4) Update local record
            self.write(
                {
                    "documenso_document_id": str(documenso_doc_id),
                    "state": "sent",
                }
            )

            _logger.info(
                "Sent document to Documenso: doc_id=%s, request_id=%s, " "signers=%d",
                documenso_doc_id,
                self.id,
                len(self.signer_ids),
            )

    def action_cancel(self):
        """Cancel the signature request."""
        self.ensure_one()
        if self.state not in ("draft", "sent"):
            raise UserError(_("Only draft or sent requests can be cancelled."))
        self.write({"state": "cancelled"})

    def action_reset_to_draft(self):
        """Reset a cancelled request back to draft."""
        self.ensure_one()
        if self.state != "cancelled":
            raise UserError(_("Only cancelled requests can be reset to draft."))
        self.write(
            {
                "state": "draft",
                "documenso_document_id": False,
                "signed_pdf_file": False,
                "signed_pdf_filename": False,
            }
        )

    # ------------------------------------------------------------------
    # Manual status check
    # ------------------------------------------------------------------

    def action_check_status(self):
        """Button action: manually poll Documenso for the signing status.

        Downloads the signed PDF automatically when the document is
        fully signed (COMPLETED).
        """
        self.ensure_one()
        if self.state != "sent":
            raise UserError(
                _("You can only check status for requests in 'Sent' state.")
            )
        try:
            self._poll_documenso_status()
        except Exception as e:
            _logger.exception(
                "Error checking Documenso status for request id=%s", self.id
            )
            raise UserError(
                _("Failed to retrieve status from Documenso: %s") % str(e)
            ) from e
        if self.state == "signed":
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Document Signed"),
                    "message": _(
                        "All signers have completed signing. "
                        "The signed PDF has been downloaded."
                    ),
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Status Updated"),
                    "message": _(
                        "Document is still awaiting signatures. " "Current status: %s"
                    )
                    % self.state,
                    "type": "warning",
                    "sticky": False,
                },
            }

    # ------------------------------------------------------------------
    # Status polling (cron)
    # ------------------------------------------------------------------

    @api.model
    def cron_update_signature_status(self):
        """Cron job: poll Documenso for status updates on sent documents.

        For each sent request, check if the document has been fully signed.
        If so, download the signed PDF and set state = 'signed'.
        """
        sent_requests = self.search([("state", "=", "sent")])
        for request in sent_requests:
            try:
                request._poll_documenso_status()
            except Exception:
                _logger.exception(
                    "Error polling Documenso status for request id=%s",
                    request.id,
                )

    # Valid selection values for the signing_status field
    _VALID_SIGNING_STATUSES = {
        "PENDING",
        "SENT",
        "OPENED",
        "SIGNED",
        "DECLINED",
        "CANCELLED",
    }

    def _poll_documenso_status(self):
        """Check Documenso API for the current status of this document."""
        self.ensure_one()
        if not self.documenso_document_id:
            return

        with self.backend_id.work_on("documenso.signature.request") as work:
            adapter = work.component(usage="backend.adapter")

            doc_data = adapter.get_document(self.documenso_document_id)
            status = doc_data.get("status", "").upper()

            # Update individual signer statuses
            recipients = doc_data.get("recipients") or doc_data.get("signers") or []
            for recipient in recipients:
                email = recipient.get("email", "")
                r_status = (
                    recipient.get("status") or recipient.get("signingStatus", "")
                ).upper()
                signer = self.signer_ids.filtered(lambda s: s.partner_id.email == email)
                if signer and r_status:
                    if r_status in self._VALID_SIGNING_STATUSES:
                        signer[0].write({"signing_status": r_status})
                    else:
                        _logger.warning(
                            "Documenso returned unrecognised signing status '%s' "
                            "for recipient %s — skipping field update.",
                            r_status,
                            email,
                        )

            if status == "COMPLETED":
                # Download the signed PDF
                signed_pdf = adapter.download_signed_document(
                    self.documenso_document_id
                )
                if signed_pdf:
                    self.write(
                        {
                            "state": "signed",
                            "signed_pdf_file": base64.b64encode(signed_pdf),
                            "signed_pdf_filename": "signed_%s"
                            % (self.pdf_filename or "document.pdf"),
                        }
                    )
                    _logger.info(
                        "Document id=%s (request id=%s) fully signed. "
                        "Downloaded signed PDF.",
                        self.documenso_document_id,
                        self.id,
                    )
                else:
                    self.write({"state": "signed"})
                    _logger.info(
                        "Document id=%s (request id=%s) fully signed. "
                        "Signed PDF download not available.",
                        self.documenso_document_id,
                        self.id,
                    )
            elif status == "CANCELLED":
                self.write({"state": "cancelled"})
                _logger.info(
                    "Document id=%s (request id=%s) was cancelled on Documenso.",
                    self.documenso_document_id,
                    self.id,
                )

    # ------------------------------------------------------------------
    # Webhook endpoint
    # ------------------------------------------------------------------

    @api.model
    def process_webhook(self, payload):
        """Process incoming webhook from Documenso.

        Called by a controller endpoint. The payload typically contains:

        * ``event``: e.g. ``DOCUMENT_COMPLETED``, ``DOCUMENT_SIGNED``
        * ``data.id``: Documenso document ID
        * ``data.recipients``: list of signer objects with their statuses

        :param payload: dict from the webhook JSON body
        """
        event = payload.get("event", "")
        data = payload.get("data") or payload.get("document") or {}
        doc_id = str(data.get("id", ""))

        if not doc_id:
            _logger.warning("Documenso webhook: no document ID in payload.")
            return

        request = self.search(
            [("documenso_document_id", "=", doc_id), ("state", "=", "sent")],
            limit=1,
        )
        if not request:
            _logger.warning(
                "Documenso webhook: no matching sent request for doc_id=%s",
                doc_id,
            )
            return

        _logger.info(
            "Processing Documenso webhook event=%s for doc_id=%s (request id=%s)",
            event,
            doc_id,
            request.id,
        )

        # Update signer statuses
        recipients = data.get("recipients") or data.get("signers") or []
        for recipient in recipients:
            email = recipient.get("email", "")
            r_status = (
                recipient.get("status") or recipient.get("signingStatus", "")
            ).upper()
            signer = request.signer_ids.filtered(lambda s: s.partner_id.email == email)
            if signer and r_status:
                if r_status in self._VALID_SIGNING_STATUSES:
                    signer[0].write({"signing_status": r_status})
                else:
                    _logger.warning(
                        "Documenso webhook: unrecognised signing status '%s' "
                        "for recipient %s — skipping field update.",
                        r_status,
                        email,
                    )

        if event in ("DOCUMENT_COMPLETED", "document.completed"):
            request._poll_documenso_status()
        elif event in ("DOCUMENT_CANCELLED", "document.cancelled"):
            request.write({"state": "cancelled"})
