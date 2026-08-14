# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDocumensoBackend(YamlTransactionCase):
    """Scenario tests for ``documenso.backend``.

    Covers create/write/archive/activate/unlink, and the ``copy_data()``
    guard that clears ``api_key`` on ``copy()`` -- ``copy()`` succeeds
    with an empty ``api_key`` since that field is no longer
    ``required=True`` at the ORM level (kept required only on the form
    view). The required field negative path for ``base_url`` is also
    covered; ``api_key`` no longer has an ORM-level negative path since
    it is not required at that level anymore. The
    ``documenso.backend.adapter`` component and
    ``action_test_connection`` are intentionally out of scope for this
    test: both perform outbound HTTP calls, which would require
    mock/patch (P6, L-15) that is out of scope for this backlog item.
    """

    def test_documenso_backend(self):
        """Run the CRUD, archive, copy and negative path scenarios."""
        self.run_yaml_scenario("test_data_documenso_backend.yaml")
