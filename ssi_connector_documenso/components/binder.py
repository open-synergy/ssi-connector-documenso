# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Documenso Binder
================

Base binder for all Documenso binding models.  Concrete binders
(e.g. for res.partner) should inherit this class and set ``_apply_on``.
"""

from odoo.addons.component.core import AbstractComponent


class DocumensoBinder(AbstractComponent):
    """Base binder for Documenso connector."""

    _name = "documenso.binder"
    _inherit = "base.binder"
    _collection = "documenso.backend"

    _external_field = "documenso_id"
    _backend_field = "backend_id"
    _odoo_field = "odoo_id"
    _sync_date_field = "sync_date"
