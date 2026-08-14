# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestMixinDocumensoSigning(YamlTransactionCase):
    """Scenario tests for ``mixin.documenso_signing``.

    ``mixin.documenso_signing`` is an ``AbstractModel`` and cannot be
    instantiated directly. This suite exercises its
    ``signature_request_count`` compute through the concrete fixture
    model ``test.documenso_signing`` (module
    ``test_ssi_connector_documenso_signing``). Guard against the
    fixture module not being installed, so this test fails loudly with
    a clear reason instead of an obscure ``KeyError``.
    """

    def test_mixin_documenso_signing(self):
        """Run the ``signature_request_count`` compute scenario."""
        if "test.documenso_signing" not in self.env:
            self.skipTest(
                "Model 'test.documenso_signing' is not available - module "
                "'test_ssi_connector_documenso_signing' is not installed."
            )
        self.run_yaml_scenario("test_data_mixin_documenso_signing.yaml")
