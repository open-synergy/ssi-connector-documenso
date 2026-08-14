# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Documenso Connector",
    "version": "14.0.1.1.0",
    "category": "Connector",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "connector",
        "ssi_connector",
        "web_tour",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "views/assets.xml",
        "views/documenso_backend_views.xml",
    ],
    "installable": True,
}
