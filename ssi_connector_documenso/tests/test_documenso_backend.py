# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestDocumensoBackend(YamlTransactionCase):
    """Scenario tests for ``documenso.backend``.

    Covers create/write/archive/activate/unlink, and the ``copy_data()``
    guard that clears ``api_key`` on ``copy()`` -- ``copy()`` succeeds
    with an empty ``api_key`` since that field is no longer
    ``required=True`` at the ORM level (kept required only on the form
    view). ``api_key`` no longer has an ORM-level negative path since it
    is not required at that level anymore. The required field negative
    path for ``base_url`` is covered in pure Python below (``P5``,
    ``L-22``): Odoo does not raise ``ValidationError`` for a missing
    required ``Char`` field at the ORM level, it lets the ``NOT NULL``
    column constraint reject the ``INSERT``, so the actual exception is
    ``psycopg2.IntegrityError`` -- a type ``expect_error`` in YAML
    cannot express. The ``documenso.backend.adapter`` component and
    ``action_test_connection`` are intentionally out of scope for this
    test: both perform outbound HTTP calls, which would require
    mock/patch (P6, L-15) that is out of scope for this backlog item.
    """

    def test_documenso_backend(self):
        """Run the CRUD, archive and copy scenarios."""
        self.run_yaml_scenario("test_data_documenso_backend.yaml")

    @mute_logger("odoo.sql_db")
    def test_create_without_base_url_rejected(self):
        """Reject create without ``base_url`` at the database level.

        Pure Python -- trigger P5 (L-22: ``psycopg2.IntegrityError`` is
        outside the 12 error types ``expect_error`` understands).
        ``base_url`` stays ``required=True`` in Python, so Postgres
        rejects the ``INSERT`` with a ``NOT NULL`` violation, raised as
        ``psycopg2.IntegrityError`` rather than ``ValidationError``.
        ``mute_logger("odoo.sql_db")`` silences the PostgreSQL ``ERROR``
        line this deliberately triggers, so ``oca_checklog_odoo`` does
        not fail the CI build over an intentional negative-path test.
        """
        with self.assertRaises(IntegrityError):
            self.env["documenso.backend"].create(
                {
                    "name": "TEST DOCUMENSO BACKEND No Base URL",
                    "api_key": "TEST-API-KEY-NO-URL",
                    "version": "v2",
                }
            )
