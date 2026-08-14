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

    def test_action_create_signing_request_returns_wizard_action(self):
        """Assert the wizard action returned by the create-request action.

        Covers ``action_create_signing_request``. Pure Python -- trigger
        P1 (L-01: ``action: call`` discards the return value, so YAML
        cannot assert it; L-02: the "actual" side of every YAML assert
        is a dotted ``getattr`` on a record, never a free-standing dict,
        so the returned ``ir.actions.act_window`` dict itself is out of
        YAML's reach).
        """
        if "test.documenso_signing" not in self.env:
            self.skipTest(
                "Model 'test.documenso_signing' is not available - module "
                "'test_ssi_connector_documenso_signing' is not installed."
            )
        host = self.env["test.documenso_signing"].create(
            {"name": "Test Create Signing Request Action"}
        )
        action = host.action_create_signing_request()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "create_documenso_signature_request")
        self.assertEqual(action["target"], "new")
        self.assertEqual(
            action["context"]["default_res_model"], "test.documenso_signing"
        )
        self.assertEqual(action["context"]["default_res_id"], host.id)

    def test_action_open_signature_requests_returns_domain(self):
        """Assert the act_window dict from ``action_open_signature_requests``.

        Pure Python -- trigger P1 (L-01: ``action: call`` discards the
        return value; L-02: the returned ``ir.actions.act_window`` dict,
        including its ``domain``, is not a record attribute so YAML's
        dotted ``getattr`` assert cannot reach it).
        """
        if "test.documenso_signing" not in self.env:
            self.skipTest(
                "Model 'test.documenso_signing' is not available - module "
                "'test_ssi_connector_documenso_signing' is not installed."
            )
        host = self.env["test.documenso_signing"].create(
            {"name": "Test Open Signature Requests Action"}
        )
        action = host.action_open_signature_requests()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "documenso.signature.request")
        self.assertIn(("res_model", "=", "test.documenso_signing"), action["domain"])
        self.assertIn(("res_id", "=", host.id), action["domain"])

    def test_action_on_multi_record_raises_ensure_one(self):
        """Reject a multi-record call with ``ValueError`` from ``ensure_one``.

        Pure Python -- trigger P1 (L-01: ``action: call`` discards the
        return value, so a raised exception on a multi-record call site
        cannot be observed through a YAML ``call`` step either).
        """
        if "test.documenso_signing" not in self.env:
            self.skipTest(
                "Model 'test.documenso_signing' is not available - module "
                "'test_ssi_connector_documenso_signing' is not installed."
            )
        Host = self.env["test.documenso_signing"]
        hosts = Host.create(
            [
                {"name": "Test Multi Record A"},
                {"name": "Test Multi Record B"},
            ]
        )
        with self.assertRaises(ValueError):
            hosts.action_open_signature_requests()
