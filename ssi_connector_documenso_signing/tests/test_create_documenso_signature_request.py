# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCreateDocumensoSignatureRequest(YamlTransactionCase):
    """Scenario tests for the ``create_documenso_signature_request`` wizard.

    Covers the side effect of ``action_confirm()``: a new
    ``documenso.signature.request`` is created for the chosen template
    and source document. The dict returned by ``action_confirm()``
    itself is out of scope for this suite (``action: call``/``wizard``
    discards return values -- ``L-01``); only its side effect on the
    database is asserted here, which YAML can express.
    """

    def test_create_documenso_signature_request(self):
        """Run the wizard scenario that creates a signature request."""
        self.run_yaml_scenario("test_data_create_documenso_signature_request.yaml")
