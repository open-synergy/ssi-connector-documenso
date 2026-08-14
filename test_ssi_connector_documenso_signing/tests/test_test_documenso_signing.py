# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestTestDocumensoSigning(YamlTransactionCase):
    """Scenario test for the ``test.documenso_signing`` fixture model.

    Confirms the fixture used by
    ``ssi_connector_documenso_signing/tests/test_mixin_documenso_signing.py``
    can be created and read on its own, independent of that suite.
    """

    def test_test_documenso_signing(self):
        """Run the basic create scenario for the fixture model."""
        self.run_yaml_scenario("test_data_test_documenso_signing.yaml")
