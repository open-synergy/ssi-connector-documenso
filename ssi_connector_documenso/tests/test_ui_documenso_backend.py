# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiDocumensoBackend(HttpSavepointCase):
    """UI/UX tour tests for the ``documenso.backend`` work instructions.

    Every ``test_*`` method runs the tour paired with the IK file named
    in its docstring (``docs/documenso_backend/NN-*.md``). Pre-Condition
    data of those IK files is prepared here in Python -- never through
    UI steps -- so that each tour only walks the click-flow the IK
    documents.
    """

    @classmethod
    def setUpClass(cls):
        """Prepare the IK Pre-Conditions shared by the documenso.backend
        tours.

        Covers the ``Access`` Pre-Condition shared by every IK file
        (admin is put in the ``Connector Manager`` group), plus the
        backend records the edit, delete, deactivate, activate and
        test-connection tours act on.
        """
        super().setUpClass()

        cls.user_admin = cls.env.ref("base.user_admin")
        cls.group_connector_manager = cls.env.ref("connector.group_connector_manager")
        cls.group_connector_manager.sudo().write(
            {
                "users": [(4, cls.user_admin.id)],
            }
        )

        cls.backend_edit = cls._create_backend("TOUR DOCUMENSO BACKEND Edit")
        cls.backend_delete = cls._create_backend("TOUR DOCUMENSO BACKEND Delete")
        cls.backend_deactivate = cls._create_backend(
            "TOUR DOCUMENSO BACKEND Deactivate"
        )
        cls.backend_activate = cls._create_backend(
            "TOUR DOCUMENSO BACKEND Activate",
            active=False,
        )
        cls.backend_test_connection = cls._create_backend(
            "TOUR DOCUMENSO BACKEND Test Connection",
            # Port 1 on loopback refuses the connection immediately,
            # without needing outbound network access -- this keeps the
            # tour from ever calling a real Documenso instance, per the
            # 06-test-connection.md IK ("does not call Documenso for
            # real").
            base_url="http://127.0.0.1:1",
        )

    @classmethod
    def _create_backend(cls, name, active=True, base_url="https://example.com"):
        """Create a ``documenso.backend`` record for tour Pre-Condition.

        :param str name: Name of the backend record.
        :param bool active: Whether the record starts active.
        :param str base_url: Value of the ``base_url`` field.
        :return: The created ``documenso.backend`` record.
        :rtype: :class:`odoo.models.Model`
        """
        return cls.env["documenso.backend"].create(
            {
                "name": name,
                "base_url": base_url,
                "api_key": "TOUR-DUMMY-API-KEY",
                "version": "v2",
                "active": active,
            }
        )

    def test_create(self):
        """Run the create tour for ``documenso.backend``.

        IK: docs/documenso_backend/01-create.md
        """
        self.start_tour(
            "/web", "ssi_connector_documenso_documenso_backend_create", login="admin"
        )

    def test_edit(self):
        """Run the edit tour for ``documenso.backend``.

        IK: docs/documenso_backend/02-edit.md
        """
        self.start_tour(
            "/web", "ssi_connector_documenso_documenso_backend_edit", login="admin"
        )

    def test_delete(self):
        """Run the delete tour for ``documenso.backend``.

        IK: docs/documenso_backend/03-delete.md
        """
        self.start_tour(
            "/web", "ssi_connector_documenso_documenso_backend_delete", login="admin"
        )

    def test_deactivate(self):
        """Run the deactivate tour for ``documenso.backend``.

        IK: docs/documenso_backend/04-deactivate.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_documenso_backend_deactivate",
            login="admin",
        )

    def test_activate(self):
        """Run the activate tour for ``documenso.backend``.

        The IK Flow ends after clicking Unarchive, without a confirm
        step -- 14.0 shows no confirmation dialog for Unarchive, see the
        comment in the tour file.

        IK: docs/documenso_backend/05-activate.md
        """
        self.start_tour(
            "/web", "ssi_connector_documenso_documenso_backend_activate", login="admin"
        )

    def test_test_connection(self):
        """Run the Test Connection tour for ``documenso.backend``.

        The record's ``base_url`` points to a loopback port that
        refuses the connection immediately, so ``action_test_connection``
        always takes the failure branch and the tour never depends on
        outbound network access. It only verifies that the button can
        be clicked and that a message is shown afterwards; the message
        content is not asserted -- that is unit test territory.

        IK: docs/documenso_backend/06-test-connection.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_documenso_documenso_backend_test_connection",
            login="admin",
        )
