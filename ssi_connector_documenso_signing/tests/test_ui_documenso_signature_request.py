# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiDocumensoSignatureRequest(HttpSavepointCase):
    """UI/UX tour tests for the ``documenso.signature.request`` work
    instructions.

    Every ``test_*`` method runs the tour paired with the IK file named
    in its docstring (``docs/documenso_signature_request/NN-*.md``).
    Pre-Condition data of those IK files is prepared here in Python --
    never through UI steps -- so that each tour only walks the
    click-flow the IK documents. Only the create flow has a tour; per
    the design decision on GitHub issue #6, ``action_send_to_documenso``
    and ``action_check_status`` call the Documenso service over the
    network and are therefore out of scope for automated UI testing.
    """

    @classmethod
    def setUpClass(cls):
        """Prepare the IK Pre-Conditions the create tour needs.

        Creates an active ``documenso.backend`` (picked automatically by
        the form's default), a ``res.partner`` to sign as, and an
        ``ir.actions.report`` registered as a py3o PDF report for
        ``res.partner`` (matching the Source Model typed by the tour) so
        the Py3o Report dropdown has a matching option.
        """
        super().setUpClass()

        cls.backend = cls.env["documenso.backend"].create(
            {
                "name": "TOUR DOCUMENSO SIGNATURE REQUEST BACKEND",
                "base_url": "https://example.com",
                "api_key": "TOUR-DUMMY-API-KEY",
                "version": "v2",
            }
        )
        cls.signer_partner = cls.env["res.partner"].create(
            {
                "name": "TOUR Documenso Signer",
                "email": "tour.documenso.signer@example.com",
            }
        )
        cls.py3o_report = cls.env["ir.actions.report"].create(
            {
                "name": "TOUR Documenso Signature Request Report",
                "model": "res.partner",
                "report_type": "py3o",
                "report_name": "tour_documenso_signature_request_report",
                "py3o_filetype": "pdf",
            }
        )

    def test_create(self):
        """Run the create tour for ``documenso.signature.request``.

        IK: docs/documenso_signature_request/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_signing_documenso_signature_request_create",
            login="admin",
        )
