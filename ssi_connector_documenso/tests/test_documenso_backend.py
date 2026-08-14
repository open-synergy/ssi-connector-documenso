# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDocumensoBackend(YamlTransactionCase):
    """Scenario tests for ``documenso.backend``.

    Covers create/write/archive/activate/unlink, the ``copy_data()``
    guard that clears ``api_key`` on ``copy()``, and the two required
    field negative paths (``base_url``, ``api_key``). The
    ``documenso.backend.adapter`` component and
    ``action_test_connection`` are intentionally out of scope for this
    test: both perform outbound HTTP calls, which would require
    mock/patch (P6, L-15) that is out of scope for this backlog item.
    """

    def test_documenso_backend(self):
        """Run the CRUD, archive, copy and negative path scenarios."""
        self.run_yaml_scenario("test_data_documenso_backend.yaml")
