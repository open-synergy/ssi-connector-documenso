# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestDocumensoSignatureRequest(YamlTransactionCase):
    """Scenario tests for ``documenso.signature.request``.

    Covers the ``_compute_allowed_py3o_report_ids`` and
    ``_compute_res_name`` computes, the ``signer_count`` compute, the
    ``signing_template_id`` cascade onchange (and clearing it), and the
    ``action_cancel``/``action_reset_to_draft`` state transitions. Uses a
    freshly created ``res.partner`` (not demo data) as the source
    document so the scenario has a real record for ``res_model``/
    ``res_id`` without depending on any other module. Out of scope, per
    the GitHub issue #14 Design Decision: ``action_generate_pdf``,
    ``action_send_to_documenso``, and ``action_check_status`` all touch
    the network or ``components/adapter.py``/``controllers/main.py``,
    which would require mock/patch (P6, L-15) or ``HttpCase`` (P7,
    L-19). The required-``backend_id`` negative path is covered in pure
    Python below (``P5``, ``L-22``): like
    ``documenso.backend.base_url`` (see
    ``ssi_connector_documenso/tests/test_documenso_backend.py``), Odoo
    does not raise ``ValidationError`` for a missing required
    ``Many2one`` field at the ORM level -- it lets the ``NOT NULL``
    foreign-key column constraint reject the ``INSERT``, so the actual
    exception is ``psycopg2.IntegrityError``, a type ``expect_error`` in
    YAML cannot express.
    """

    def test_documenso_signature_request(self):
        """Run the compute, onchange and state transition scenarios."""
        self.run_yaml_scenario("test_data_documenso_signature_request.yaml")

    @mute_logger("odoo.sql_db")
    def test_create_without_backend_id_rejected(self):
        """Reject create without ``backend_id`` at the database level.

        Pure Python -- trigger P5 (L-22: ``psycopg2.IntegrityError`` is
        outside the 12 error types ``expect_error`` understands).
        ``backend_id`` is ``required=True`` and has a default that looks
        up an active ``documenso.backend``, so ``backend_id: False`` is
        passed explicitly to override that default and force a ``NULL``
        insert. Postgres then rejects it with a ``NOT NULL`` violation,
        raised as ``psycopg2.IntegrityError`` rather than
        ``ValidationError``. ``mute_logger("odoo.sql_db")`` silences the
        PostgreSQL ``ERROR`` line this deliberately triggers, so
        ``oca_checklog_odoo`` does not fail the CI build over an
        intentional negative-path test.
        """
        partner = self.env["res.partner"].create(
            {"name": "TEST DOCUMENSO REQUEST No Backend Partner"}
        )
        report = self.env["ir.actions.report"].create(
            {
                "name": "TEST DOCUMENSO REQUEST No Backend Report",
                "model": "res.partner",
                "report_type": "py3o",
                "report_name": "test_documenso_request_no_backend_report",
                "py3o_filetype": "pdf",
            }
        )
        with self.assertRaises(IntegrityError):
            self.env["documenso.signature.request"].create(
                {
                    "backend_id": False,
                    "res_model": "res.partner",
                    "res_id": partner.id,
                    "py3o_report_id": report.id,
                }
            )
