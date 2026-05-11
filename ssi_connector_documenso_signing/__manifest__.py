# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Documenso Connector - Signing",
    "version": "14.0.1.2.0",
    "category": "Connector",
    "summary": "Generate PDF documents via py3o and send to Documenso for "
    "digital signatures with multi-signer support.",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "ssi_connector_documenso",
        "report_py3o",
        "queue_job",
        "ssi_decorator",
        "ssi_localdict_mixin",
        "ssi_master_data_mixin",
    ],
    "external_dependencies": {
        "python": [
            "fitz",
        ]
    },
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "templates/signing_request_templates.xml",
        "views/documenso_signing_template_views.xml",
        "views/documenso_signature_request_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
