# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiDocumensoSigningTemplate(HttpSavepointCase):
    """UI/UX tour tests for the ``documenso.signing.template`` work
    instructions.

    Every ``test_*`` method runs the tour paired with the IK file named
    in its docstring (``docs/documenso_signing_template/NN-*.md``).
    Pre-Condition data of those IK files is prepared here in Python --
    never through UI steps -- so that each tour only walks the
    click-flow the IK documents.
    """

    @classmethod
    def setUpClass(cls):
        """Prepare the IK Pre-Conditions shared by the documenso.signing_template
        tours.

        Covers the ``Access`` Pre-Condition shared by every IK file
        (admin is put in the ``Connector Manager`` group), a py3o PDF
        report registered for ``res.partner`` so the create tour's Py3o
        Report dropdown has a matching option, and the signing template
        records the edit, delete, deactivate and activate tours act on.
        """
        super().setUpClass()

        cls.user_admin = cls.env.ref("base.user_admin")
        cls.group_connector_manager = cls.env.ref("connector.group_connector_manager")
        cls.group_connector_manager.sudo().write(
            {
                "users": [(4, cls.user_admin.id)],
            }
        )

        cls.py3o_report = cls.env["ir.actions.report"].create(
            {
                "name": "TOUR Documenso Signing Template Report",
                "model": "res.partner",
                "report_type": "py3o",
                "report_name": "tour_documenso_signing_template_report",
                "py3o_filetype": "pdf",
            }
        )

        cls.template_edit = cls._create_template("TOUR DOCUMENSO SIGNING TEMPLATE Edit")
        cls.template_delete = cls._create_template(
            "TOUR DOCUMENSO SIGNING TEMPLATE Delete"
        )
        cls.template_deactivate = cls._create_template(
            "TOUR DOCUMENSO SIGNING TEMPLATE Deactivate"
        )
        cls.template_activate = cls._create_template(
            "TOUR DOCUMENSO SIGNING TEMPLATE Activate",
            active=False,
        )

    @classmethod
    def _create_template(cls, name, res_model="res.partner", active=True):
        """Create a ``documenso.signing.template`` record for tour
        Pre-Condition.

        Includes one signer template line so the edit tour has an
        existing row to open and change.

        :param str name: Name of the signing template record.
        :param str res_model: Value of the ``res_model`` field.
        :param bool active: Whether the record starts active.
        :return: The created ``documenso.signing.template`` record.
        :rtype: :class:`odoo.models.Model`
        """
        return cls.env["documenso.signing.template"].create(
            {
                "name": name,
                "code": "/",
                "res_model": res_model,
                "active": active,
                "signer_template_ids": [
                    (
                        0,
                        0,
                        {
                            "role": "SIGNER",
                            "signing_order": 1,
                            "signature_anchor": "{{SIGN_1}}",
                            "partner_code": "document.partner_id",
                        },
                    )
                ],
            }
        )

    def test_create(self):
        """Run the create tour for ``documenso.signing.template``.

        IK: docs/documenso_signing_template/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_signing_documenso_signing_template_create",
            login="admin",
        )

    def test_edit(self):
        """Run the edit tour for ``documenso.signing.template``.

        IK: docs/documenso_signing_template/02-edit.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_signing_documenso_signing_template_edit",
            login="admin",
        )

    def test_delete(self):
        """Run the delete tour for ``documenso.signing.template``.

        IK: docs/documenso_signing_template/03-delete.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_signing_documenso_signing_template_delete",
            login="admin",
        )

    def test_deactivate(self):
        """Run the deactivate tour for ``documenso.signing.template``.

        IK: docs/documenso_signing_template/04-deactivate.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_signing_documenso_signing_template_deactivate",
            login="admin",
        )

    def test_activate(self):
        """Run the activate tour for ``documenso.signing.template``.

        IK: docs/documenso_signing_template/05-activate.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_signing_documenso_signing_template_activate",
            login="admin",
        )
