# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestDocumensoSigningTemplate(YamlTransactionCase):
    """Scenario tests for ``documenso.signing.template``.

    Covers create/write/unlink, archive/restore, the
    ``_compute_allowed_py3o_report_ids`` compute (matching and
    non-matching ``res_model``), and the ``onchange_py3o_report_id``
    onchange. The required-``name`` negative path is covered in pure
    Python below (``P5``, ``L-22``): like ``documenso.backend.base_url``
    (see ``ssi_connector_documenso/tests/test_documenso_backend.py``),
    Odoo does not raise ``ValidationError`` for a missing required
    ``Char`` field at the ORM level -- it lets the ``NOT NULL`` column
    constraint reject the ``INSERT``, so the actual exception is
    ``psycopg2.IntegrityError``, a type ``expect_error`` in YAML cannot
    express.
    """

    def test_documenso_signing_template(self):
        """Run the CRUD, archive, compute and onchange scenarios."""
        self.run_yaml_scenario("test_data_documenso_signing_template.yaml")

    @mute_logger("odoo.sql_db")
    def test_create_without_name_rejected(self):
        """Reject create without ``name`` at the database level.

        Pure Python -- trigger P5 (L-22: ``psycopg2.IntegrityError`` is
        outside the 12 error types ``expect_error`` understands).
        ``name`` is ``required=True`` in Python with no default, so
        Postgres rejects the ``INSERT`` with a ``NOT NULL`` violation,
        raised as ``psycopg2.IntegrityError`` rather than
        ``ValidationError``. ``mute_logger("odoo.sql_db")`` silences the
        PostgreSQL ``ERROR`` line this deliberately triggers, so
        ``oca_checklog_odoo`` does not fail the CI build over an
        intentional negative-path test.
        """
        with self.assertRaises(IntegrityError):
            self.env["documenso.signing.template"].create(
                {
                    "code": "TEST-TEMPLATE-NO-NAME",
                    "res_model": "res.partner",
                }
            )
