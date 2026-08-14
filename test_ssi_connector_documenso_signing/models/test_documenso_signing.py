# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TestDocumensoSigning(models.Model):
    """Concrete fixture model exercising ``mixin.documenso_signing``.

    ``mixin.documenso_signing`` is an ``AbstractModel`` -- it has no
    database table of its own, so its ``signature_request_count`` compute
    cannot be exercised without a real inheriting model. This module has
    no such model of its own (it only defines the mixin for other,
    downstream modules to inherit), so this fixture provides a minimal
    concrete host, following the same pattern already used in this
    monorepo family for ``mixin.master_data``
    (``ssi_master_data_mixin``/``test_ssi_master_data_mixin``) and
    ``mixin.decorator`` (``ssi_decorator``/``test_ssi_decorator``).
    """

    _name = "test.documenso_signing"
    _description = "Test Documenso Signing"
    _inherit = [
        "mixin.documenso_signing",
        "mail.thread",
    ]

    name = fields.Char(
        string="Name",
        required=True,
    )
