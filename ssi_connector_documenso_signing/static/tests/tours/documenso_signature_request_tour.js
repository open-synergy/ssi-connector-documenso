// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_connector_documenso_signing.documenso_signature_request_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Flow 1 of docs/documenso_signature_request/01-create.md: "Open the
        // Connector > Documenso > Signing > Signature Requests menu."
        //
        // The path has four levels but only three are clickable. "Connector" is
        // the app icon. "Documenso" (menu_documenso_root) is a direct child of
        // the app root, so it is always rendered as its own top-nav dropdown
        // section even though it carries no action of its own. "Signing"
        // (menu_documenso_signing) is one level deeper, has no action, and does
        // have children ("Signing Templates", "Signature Requests") -- 14.0
        // therefore renders it as a .dropdown-header with no data-menu-xmlid and
        // flattens "Signature Requests" into the same "Documenso" dropdown
        // (odoo-development-ui-test patterns.md §A, same mechanic already used
        // by ssi_connector_documenso/documenso_backend_tour.js for "Documenso
        // Configuration").
        function openDocumensoSignatureRequestList() {
            return [
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Open the Connector app",
                    trigger:
                        '.o_app[data-menu-xmlid="ssi_connector.menu_root_connector"]',
                },
                {
                    content: "Open the Documenso menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso.menu_documenso_root"]',
                },
                {
                    content: "Open the Signature Requests menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso_signing.menu_documenso_signature_requests"]',
                },
                {
                    // Gate: wait for the TARGET action to be installed, not just
                    // for "a list is on screen" (odoo-development-ui-test
                    // patterns.md §A).
                    content: "Signature Requests list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Signature Requests)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ];
        }

        // IK: docs/documenso_signature_request/01-create.md
        tour.register(
            "ssi_connector_documenso_signing_documenso_signature_request_create",
            {
                test: true,
                url: "/web",
            },
            [].concat(
                // ── Flow 1 — Open the Signature Requests menu.
                openDocumensoSignatureRequestList(),
                [
                    // ── Flow 2 — Click the New button.
                    {
                        content: "Click Create",
                        trigger: ".o_list_button_add",
                        extra_trigger: ".o_list_view",
                    },
                    {
                        content: "Form is open in edit mode",
                        trigger: ".o_form_view.o_form_editable",
                        run: function () {
                            // Assertion only.
                        },
                    },

                    // ── Flow 3 — Fill in the fields. Documenso Backend and
                    // Company are left at their auto-filled defaults and are not
                    // touched, per the IK ("Automatically filled ... Change if
                    // needed."). Signing Template is left empty, per the IK's
                    // "leave empty to fill everything manually" branch, so
                    // Source Model / Source Record ID / Py3o Report are typed by
                    // hand below.
                    {
                        content: "Fill in Source Model",
                        trigger: ".o_field_widget[name='res_model']",
                        extra_trigger: ".o_form_view.o_form_editable",
                        run: "text res.partner",
                    },
                    {
                        // Source Record ID is a plain Integer field with no
                        // foreign-key constraint at the database level -- the
                        // model only browses it (inside a broad try/except) when
                        // computing the display name, and when Generate PDF /
                        // Send to Documenso actually run. Neither happens in this
                        // create-only tour (see the Generate PDF step below), so
                        // any integer satisfies the IK's Pre-Condition for this
                        // automated run without depending on a specific record
                        // ID existing in the test database.
                        content: "Fill in Source Record ID",
                        trigger: ".o_field_widget[name='res_id']",
                        run: "text 1",
                    },
                    {
                        // Selecting the Source Model recomputes the
                        // allowed_py3o_report_ids domain (@api.depends
                        // "res_model"), so the Py3o Report dropdown only offers
                        // reports registered for "res.partner" -- the test
                        // report created in setUpClass.
                        content: "Select the Py3o Report",
                        trigger: ".o_field_many2one[name='py3o_report_id'] input",
                        run: "text TOUR Documenso Signature Request Report",
                    },
                    {
                        content: "Pick the Py3o Report from the dropdown",
                        trigger:
                            ".ui-autocomplete .ui-menu-item a:contains(TOUR Documenso Signature Request Report)",
                        in_modal: false,
                    },

                    // ── Flow 4 — Add a line on the Signers tab.
                    {
                        content: "Open the Signers tab",
                        trigger: ".o_notebook .nav-link:contains(Signers)",
                    },
                    {
                        content: "Click Add a line",
                        trigger: ".o_field_x2many .o_field_x2many_list_row_add a",
                    },
                    {
                        content: "Select the Signer",
                        trigger:
                            ".o_selected_row .o_field_widget[name='partner_id'] input",
                        run: "text TOUR Documenso Signer",
                    },
                    {
                        content: "Pick the Signer from the dropdown",
                        trigger:
                            ".ui-autocomplete .ui-menu-item a:contains(TOUR Documenso Signer)",
                        in_modal: false,
                    },

                    // ── Flow 5 — Click Save. Role and Signing Order keep their
                    // defaults (Signer / 1), so the row is not touched further.
                    {
                        content: "Save the record",
                        trigger: ".o_form_button_save",
                    },
                    {
                        content: "Record is saved",
                        trigger: ".o_form_view.o_form_readonly",
                        run: function () {
                            // Assertion only.
                        },
                    },

                    // ── Flow 6 (Inline Action, action_generate_pdf) — Generate
                    // PDF is a py3o report button: odoo-development-ui-test
                    // patterns.md §Q lists report buttons among the actions a
                    // tour only approaches, never completes, since generating a
                    // real PDF needs an actual py3o template and clicking it has
                    // no DOM "done" signal a headless run can wait on. This step
                    // only proves the button is visible and clickable, per the
                    // IK ("Optionally, click Generate PDF ... not required to
                    // proceed"); it is never clicked.
                    {
                        content: "Generate PDF button is visible and enabled",
                        trigger:
                            ".o_statusbar_buttons button[name='action_generate_pdf']:enabled",
                        extra_trigger: ".o_form_view",
                        run: function () {
                            // Assertion only; do not trigger the default click
                            // action.
                        },
                    },

                    // ── Post-Condition — A new Documenso Signature Request
                    // record is created with status Draft. Verified through the
                    // statusbar state, not through field values (those belong to
                    // odoo-development-unit-test).
                    {
                        content: "Status is Draft",
                        trigger:
                            ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                        run: function () {
                            // Assertion only.
                        },
                    },
                ]
            )
        );
    }
);
