// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_connector_documenso_signing.documenso_signing_template_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // Shared navigation block reused by every tour below -- it corresponds to
        // Flow 1 of every documenso_signing_template IK: "Open the Connector >
        // Documenso > Signing > Signing Templates menu."
        //
        // The path has four levels but only three are clickable. "Connector" is
        // the app icon. "Documenso" (menu_documenso_root) is a direct child of
        // the app root, so it is always rendered as its own top-nav dropdown
        // section even though it carries no action of its own. "Signing"
        // (menu_documenso_signing) is one level deeper, has no action, and does
        // have children ("Signing Templates", "Signature Requests") -- 14.0
        // therefore renders it as a .dropdown-header with no data-menu-xmlid and
        // flattens "Signing Templates" into the same "Documenso" dropdown
        // (odoo-development-ui-test patterns.md §A, same mechanic already used
        // by documenso_signature_request_tour.js for "Signature Requests").
        function openDocumensoSigningTemplateList() {
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
                    content: "Open the Signing Templates menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso_signing.menu_documenso_signing_templates"]',
                },
                {
                    // Gate: wait for the TARGET action to be installed, not just
                    // for "a list is on screen" (odoo-development-ui-test
                    // patterns.md §A).
                    content: "Signing Templates list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Signing Templates)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ];
        }

        // Click the "Save & Close" button of the signer-template line dialog
        // opened by "Add a line" -- the nested <tree> for signer_template_ids
        // has no editable="bottom", so 14.0 opens the nested <form> as a modal
        // (web/static/src/js/views/view_dialogs.js FormViewDialog), unlike the
        // inline-editable signer_ids used by documenso_signature_request_tour.js.
        function clickSaveAndCloseSignerDialog() {
            return {
                content: "Click Save & Close on the signer template dialog",
                trigger: ".modal-footer button.btn-primary",
                run: function () {
                    var $save = $(".modal-footer button.btn-primary").filter(
                        function () {
                            return $(this).text().trim() === "Save & Close";
                        }
                    );
                    $save[0].click();
                },
            };
        }

        // IK: docs/documenso_signing_template/01-create.md
        tour.register(
            "ssi_connector_documenso_signing_documenso_signing_template_create",
            {
                test: true,
                url: "/web",
            },
            [].concat(
                // ── Flow 1 — Open the Signing Templates menu.
                openDocumensoSigningTemplateList(),
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

                    // ── Flow 3 — Fill in Name and Code (typed manually here;
                    // the "leave as / and click Generate Code" alternative is
                    // only proven reachable below, without being clicked --
                    // clicking it would fail without a sequence.template
                    // configured for this model, per the IK Pre-Condition).
                    {
                        content: "Fill in Name",
                        trigger: ".o_field_widget[name='name']",
                        extra_trigger: ".o_form_view.o_form_editable",
                        run: "text TOUR DOCUMENSO SIGNING TEMPLATE Create",
                    },
                    {
                        content: "Fill in Code",
                        trigger: ".o_field_widget[name='code']",
                        run: "text TOUR-SIGNING-TEMPLATE-CREATE",
                    },
                    {
                        // Inline Action (action_generate_code): only its
                        // presence/enabled state is proven, per
                        // odoo-development-ui-test patterns.md §Q-adjacent
                        // caution -- clicking it needs a sequence.template this
                        // test database does not configure.
                        content: "Generate Code button is visible and enabled",
                        trigger:
                            ".o_statusbar_buttons button[name='action_generate_code']:enabled",
                        run: function () {
                            // Assertion only; do not trigger the default click
                            // action.
                        },
                    },

                    // ── Flow 4 — On the Document tab, fill Source Model and
                    // select the Py3o Report.
                    {
                        content: "Open the Document tab",
                        trigger: ".o_notebook .nav-link:contains(Document)",
                    },
                    {
                        content: "Fill in Source Model",
                        trigger: ".o_field_widget[name='res_model']",
                        run: "text res.partner",
                    },
                    {
                        // Selecting Source Model recomputes
                        // allowed_py3o_report_ids (@api.depends "res_model"),
                        // so the Py3o Report dropdown only offers reports
                        // registered for "res.partner" -- the test report
                        // created in setUpClass.
                        content: "Select the Py3o Report",
                        trigger: ".o_field_many2one[name='py3o_report_id'] input",
                        run: "text TOUR Documenso Signing Template Report",
                    },
                    {
                        content: "Pick the Py3o Report from the dropdown",
                        trigger:
                            ".ui-autocomplete .ui-menu-item a:contains(TOUR Documenso Signing Template Report)",
                        in_modal: false,
                    },

                    // ── Flow 5 — On the Signer Templates tab, add a line.
                    {
                        content: "Open the Signer Templates tab",
                        trigger: ".o_notebook .nav-link:contains(Signer Templates)",
                    },
                    {
                        content: "Click Add a line",
                        trigger: ".o_field_x2many .o_field_x2many_list_row_add a",
                    },
                    {
                        // The Partner Python Code field (widget="ace") lazy-
                        // loads /web/static/lib/ace/ace.js the first time it
                        // starts (AceEditor.jsLibs), and Odoo only inserts a
                        // widget's markup into the DOM once its whole
                        // willStart()/start() chain resolves -- so the WHOLE
                        // dialog, not just this field, stays absent from the
                        // DOM until that download finishes. In CI that can
                        // take longer than the tour's 10000ms default step
                        // timeout even though nothing is actually stuck
                        // (confirmed on PR #21: the failure screenshot,
                        // captured at the default timeout, already showed the
                        // ace editor fully rendered). Raise only this gate;
                        // once it passes, ace.js is already loaded and the
                        // remaining steps in the dialog are fast.
                        content: "Signer template dialog is open",
                        trigger: ".modal .o_field_widget[name='partner_code']",
                        timeout: 30000,
                        run: function () {
                            // Assertion only.
                        },
                    },
                    {
                        // Role and Signing Order keep their defaults (Signer /
                        // 1), so only Signature Anchor and Partner Python Code
                        // are filled in.
                        content: "Fill in Signature Anchor",
                        trigger: ".modal .o_field_widget[name='signature_anchor']",
                        run: "text {{SIGN_1}}",
                    },
                    {
                        // The Partner Python Code field uses widget="ace",
                        // which renders a syntax-highlighted view backed by a
                        // hidden <textarea class="ace_text-input"> that ACE
                        // itself listens on for pasted/composed text -- setting
                        // its value and dispatching an "input" event (the tour
                        // "text" run type on a <textarea>) is the same path ACE
                        // uses for paste, so it updates the editor's document.
                        content: "Fill in Partner Python Code",
                        trigger:
                            ".modal .o_field_widget[name='partner_code'] textarea.ace_text-input",
                        run: "text document.partner_id",
                    },
                    clickSaveAndCloseSignerDialog(),
                    {
                        content: "Signer template line is added",
                        trigger:
                            ".o_field_x2many[name='signer_template_ids'] .o_data_row",
                        extra_trigger: ".o_form_view",
                        run: function () {
                            // Assertion only -- only that a row now exists is
                            // checked; its field values are unit test
                            // territory (Keputusan Desain, issue #12).
                        },
                    },

                    // ── Flow 6 — Click Save.
                    {
                        content: "Save the record",
                        trigger: ".o_form_button_save",
                    },

                    // ── Post-Condition — A new Documenso Signing Template
                    // record is created and appears in the Signing Templates
                    // list, active by default.
                    {
                        content: "Record is saved and displayed",
                        trigger:
                            ".o_control_panel .breadcrumb-item.active:contains(TOUR DOCUMENSO SIGNING TEMPLATE Create)",
                        extra_trigger: ".o_form_view.o_form_readonly",
                        run: function () {
                            // Assertion only; do not trigger the default click
                            // action.
                        },
                    },
                ]
            )
        );

        // IK: docs/documenso_signing_template/02-edit.md
        tour.register(
            "ssi_connector_documenso_signing_documenso_signing_template_edit",
            {
                test: true,
                url: "/web",
            },
            [].concat(
                // ── Flow 1 — Open the Signing Templates menu.
                openDocumensoSigningTemplateList(),
                [
                    // ── Flow 2 — Find and open the record to edit.
                    {
                        content: "Open the signing template record",
                        trigger:
                            ".o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Edit) .o_data_cell:first",
                        extra_trigger: ".o_list_view",
                    },
                    {
                        content: "Form is open",
                        trigger: ".o_form_view",
                        run: function () {
                            // Assertion only.
                        },
                    },
                    {
                        // 14.0 opens an existing record read-only, so Edit must
                        // be clicked before any field can be touched
                        // (odoo-development-ui-test patterns.md §E).
                        content: "Click the Edit button",
                        trigger: ".o_form_button_edit",
                    },
                    {
                        content: "Form is now editable",
                        trigger: ".o_form_view.o_form_editable",
                        run: function () {
                            // Assertion only.
                        },
                    },

                    // ── Flow 3 — Change Name and Source Model. Changing
                    // Source Model clears the previously selected Py3o Report
                    // (onchange_py3o_report_id) -- only the action is
                    // performed here; the cleared value itself is not
                    // asserted, per the Keputusan Desain on issue #12 ("tour
                    // tidak menguji nilai").
                    {
                        content: "Change the Name",
                        trigger: ".o_field_widget[name='name']",
                        run: "text TOUR DOCUMENSO SIGNING TEMPLATE Edit Changed",
                    },
                    {
                        content: "Open the Document tab",
                        trigger: ".o_notebook .nav-link:contains(Document)",
                    },
                    {
                        content: "Change the Source Model",
                        trigger: ".o_field_widget[name='res_model']",
                        run: "text account.move",
                    },

                    // ── Flow 4 — On the Signer Templates tab, edit the
                    // existing signer line (Signature Anchor only -- Partner
                    // Python Code already has a value from setUpClass and is
                    // left untouched).
                    {
                        content: "Open the Signer Templates tab",
                        trigger: ".o_notebook .nav-link:contains(Signer Templates)",
                    },
                    {
                        content: "Open the existing signer template line",
                        trigger:
                            ".o_field_x2many[name='signer_template_ids'] .o_data_row:first .o_data_cell:first",
                    },
                    {
                        // Same ace.js lazy-load gate as the create tour above
                        // -- raise the timeout, not the selector (PR #21 CI
                        // failure analysis).
                        content: "Signer template dialog is open",
                        trigger: ".modal .o_field_widget[name='partner_code']",
                        timeout: 30000,
                        run: function () {
                            // Assertion only.
                        },
                    },
                    {
                        content: "Change the Signature Anchor",
                        trigger: ".modal .o_field_widget[name='signature_anchor']",
                        run: "text {{SIGN_2}}",
                    },
                    clickSaveAndCloseSignerDialog(),

                    // ── Flow 5 — Click Save.
                    {
                        content: "Save the record",
                        trigger: ".o_form_button_save",
                        extra_trigger: ".o_form_view:not(:has(.modal))",
                    },

                    // ── Post-Condition — The record is updated with the new
                    // values.
                    {
                        content: "Record is saved",
                        trigger: ".o_form_view.o_form_readonly",
                        run: function () {
                            // Assertion only.
                        },
                    },
                ]
            )
        );

        // IK: docs/documenso_signing_template/03-delete.md
        tour.register(
            "ssi_connector_documenso_signing_documenso_signing_template_delete",
            {
                test: true,
                url: "/web",
            },
            [].concat(
                // ── Flow 1 — Open the Signing Templates menu.
                openDocumensoSigningTemplateList(),
                [
                    // ── Flow 2 — Select the record to delete (checkbox).
                    {
                        content: "Select the record to delete",
                        trigger:
                            ".o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Delete) " +
                            ".o_list_record_selector input",
                        run: "click",
                    },

                    // ── Flow 3 — Click Action > Delete.
                    {
                        content: "Open the Action menu",
                        trigger: ".o_cp_action_menus button:contains(Action)",
                    },
                    {
                        content: "Click Delete",
                        // The Action menu items are Owl components; match the
                        // EXACT label instead of :contains(Delete), which
                        // could pick a different item as a substring
                        // (odoo-development-ui-test patterns.md §I).
                        trigger: ".o_cp_action_menus .o_menu_item a",
                        run: function () {
                            var $delete = $(".o_cp_action_menus .o_menu_item a").filter(
                                function () {
                                    return $(this).text().trim() === "Delete";
                                }
                            );
                            $delete[0].click();
                        },
                    },

                    // ── Flow 4 — Click OK to confirm.
                    {
                        content: "Confirm deletion",
                        trigger: ".modal-footer button.btn-primary",
                        in_modal: true,
                    },

                    // ── Post-Condition — The selected record is permanently
                    // removed and no longer appears in the list.
                    {
                        content: "Record no longer appears in the list",
                        trigger:
                            ".o_list_view:not(:has(.o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Delete)))",
                        run: function () {
                            // Assertion only; do not trigger the default click
                            // action.
                        },
                    },
                ]
            )
        );

        // IK: docs/documenso_signing_template/04-deactivate.md
        tour.register(
            "ssi_connector_documenso_signing_documenso_signing_template_deactivate",
            {
                test: true,
                url: "/web",
            },
            [].concat(
                // ── Flow 1 — Open the Signing Templates menu.
                openDocumensoSigningTemplateList(),
                [
                    // ── Flow 2 — Select the record to deactivate (checkbox).
                    {
                        content: "Select the record to deactivate",
                        trigger:
                            ".o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Deactivate) " +
                            ".o_list_record_selector input",
                        run: "click",
                    },

                    // ── Flow 3 — Click Action > Archive.
                    {
                        content: "Open the Action menu",
                        trigger: ".o_cp_action_menus button:contains(Action)",
                    },
                    {
                        content: "Click Archive",
                        trigger: ".o_cp_action_menus .o_menu_item a",
                        run: function () {
                            var $archive = $(
                                ".o_cp_action_menus .o_menu_item a"
                            ).filter(function () {
                                return $(this).text().trim() === "Archive";
                            });
                            $archive[0].click();
                        },
                    },

                    // ── Flow 4 — Click OK to confirm.
                    {
                        content: "Confirm the dialog",
                        trigger: ".modal-footer button.btn-primary",
                        in_modal: true,
                    },

                    // ── Post-Condition — The record is archived and no
                    // longer appears in the default list view.
                    {
                        content: "Record no longer appears in the active list",
                        trigger:
                            ".o_list_view:not(:has(.o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Deactivate)))",
                        run: function () {
                            // Assertion only; do not trigger the default click
                            // action.
                        },
                    },
                ]
            )
        );

        // IK: docs/documenso_signing_template/05-activate.md
        tour.register(
            "ssi_connector_documenso_signing_documenso_signing_template_activate",
            {
                test: true,
                url: "/web",
            },
            [].concat(
                // ── Flow 1 — Open the Signing Templates menu.
                openDocumensoSigningTemplateList(),
                [
                    // ── Flow 2 — Enable the Archived filter in the search
                    // bar.
                    {
                        content: "Open the Filters menu",
                        // 14.0: the Filters dropdown is an Owl component whose
                        // open state does not always flip on the synthetic
                        // mouse event sequence -- use a real browser click
                        // (odoo-development-ui-test patterns.md §I/§J).
                        trigger: ".o_filter_menu .o_dropdown_toggler_btn",
                        run: function () {
                            this.$anchor[0].click();
                        },
                    },
                    {
                        content: "Enable the Archived filter",
                        trigger: ".o_filter_menu .o_menu_item a:contains(Archived)",
                        run: function () {
                            this.$anchor[0].click();
                        },
                    },

                    // ── Flow 3 — Select the record to reactivate (checkbox).
                    {
                        content: "Select the record to reactivate",
                        trigger:
                            ".o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Activate) " +
                            ".o_list_record_selector input",
                        run: "click",
                    },

                    // ── Flow 4 — Click Action > Unarchive. There is no step
                    // for a confirm dialog: 14.0 shows no dialog for
                    // Unarchive (list_controller.js _getActionMenuItems --
                    // only "Archive" wraps its callback in Dialog.confirm,
                    // while "Unarchive" calls _toggleArchiveState(false)
                    // directly), which is why the IK itself has no confirm
                    // step for this action.
                    {
                        content: "Open the Action menu",
                        trigger: ".o_cp_action_menus button:contains(Action)",
                    },
                    {
                        content: "Click Unarchive",
                        trigger: ".o_cp_action_menus .o_menu_item a",
                        run: function () {
                            var $unarchive = $(
                                ".o_cp_action_menus .o_menu_item a"
                            ).filter(function () {
                                return $(this).text().trim() === "Unarchive";
                            });
                            $unarchive[0].click();
                        },
                    },

                    // ── Post-Condition — The record is restored and belongs
                    // to the default (active) list again. With the Archived
                    // filter still on, the visible proof is that the row
                    // leaves the archived-only list.
                    {
                        content: "Record leaves the archived list",
                        trigger:
                            ".o_list_view:not(:has(.o_data_row:contains(TOUR DOCUMENSO SIGNING TEMPLATE Activate)))",
                        run: function () {
                            // Assertion only; do not trigger the default click
                            // action.
                        },
                    },
                ]
            )
        );
    }
);
