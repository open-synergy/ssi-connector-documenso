# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDocumensoSignatureSigner(YamlTransactionCase):
    """Scenario tests for ``documenso.signature.signer``.

    Covers the ``onchange_signature_anchor`` onchange: auto-filling an
    empty ``signature_anchor`` when ``partner_id`` is set, and leaving a
    manually-set ``signature_anchor`` untouched.
    """

    def test_documenso_signature_signer(self):
        """Run the onchange scenarios for the signer anchor."""
        self.run_yaml_scenario("test_data_documenso_signature_signer.yaml")
