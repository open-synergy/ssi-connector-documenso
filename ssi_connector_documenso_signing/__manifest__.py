# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Documenso Connector - Signing",
    "version": "14.0.2.0.2",
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
        "ssi_multiple_approval_mixin",
    ],
    "external_dependencies": {
        "python": [
            "fitz",
        ]
    },
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_model_access/create_documenso_signature_request.xml",
        "data/ir_cron.xml",
        "templates/signing_request_templates.xml",
        "views/documenso_signing_template_views.xml",
        "views/documenso_signature_request_views.xml",
        "views/approval_template_views.xml",
        "views/menu.xml",
        "wizards/create_documenso_signature_request.xml",
    ],
    "installable": True,
}
