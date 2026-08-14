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
        //
        // TIMEOUT NOTE (applies to every dropdown/filter/action-menu step in
        // this file, not just this block): PR #21 CI failed three times on the
        // "test with OCB" job (never on "test with Odoo") at different
        // dropdown/filter/action-menu steps each time -- "Enable the Archived
        // filter", then "Open the Action menu" on two other tours, then
        // "Enable the Archived filter" again on a later run
        // (31768379014) -- while documenso_backend_tour.js's own "Enable the
        // Archived filter" step (no explicit timeout either) stayed green on
        // every run. The OCB image (ghcr.io/oca/oca-ci/py3.6-ocb14.0) boots
        // far more addons than the plain Odoo image, and this file runs SIX
        // sequential HttpSavepointCase tour sessions against a heavier form
        // (mixin.master_data: chatter + a custom fields_view_get override) --
        // so every dropdown/menu render in this file, not one specific step,
        // is closer to the default 10000ms step timeout here than in lighter
        // tours. Steps that open a dropdown, filter menu, action menu, or
        // confirm dialog get an explicit 20000ms below; plain field fills and
        // button clicks that never failed are left at the default.
        function openDocumensoSigningTemplateList() {
            return [
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Open the Connector app",
                    trigger:
                        '.o_app[data-menu-xmlid="ssi_connector.menu_root_connector"]',
                    timeout: 20000,
                },
                {
                    content: "Open the Documenso menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso.menu_documenso_root"]',
                    timeout: 20000,
                },
                {
                    content: "Open the Signing Templates menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso_signing.menu_documenso_signing_templates"]',
                    timeout: 20000,
                },
                {
                    // Gate: wait for the TARGET action to be installed, not just
                    // for "a list is on screen" (odoo-development-ui-test
                    // patterns.md §A).
                    content: "Signing Templates list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Signing Templates)",
                    extra_trigger: ".o_list_view",
                    timeout: 20000,
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ];
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

                    // ── Flow 5 — On the Signer Templates tab, the Add a line
                    // button is proven reachable, not clicked through to a
                    // saved row. Its dialog holds the Partner Python Code
                    // field (widget="ace"), which lazy-loads
                    // /web/static/lib/ace/ace.js the first time it starts
                    // (AceEditor.jsLibs) -- and Odoo only inserts a widget's
                    // markup into the DOM once its whole
                    // willStart()/start() chain resolves, so the WHOLE
                    // dialog (not just this one field) stays absent from the
                    // DOM until that load finishes. On PR #21 CI this proved
                    // to exceed even a raised 30000ms step timeout (run
                    // 31767181081: "Click Add a line" succeeded, then the
                    // dialog gate still timed out 30s later with nothing
                    // else logged in between), so no bounded timeout on this
                    // step is reliable in this CI environment -- the same
                    // treatment as the Generate PDF button in
                    // documenso_signature_request_tour.js (patterns.md §Q):
                    // approach it, do not complete it. Adding a signer line
                    // is optional at this step per the IK (a template can be
                    // saved without one), so skipping it here does not
                    // shortcut a mandatory part of the Flow.
                    {
                        content: "Open the Signer Templates tab",
                        trigger: ".o_notebook .nav-link:contains(Signer Templates)",
                    },
                    {
                        content: "Add a line button is visible and enabled",
                        trigger:
                            ".o_field_x2many .o_field_x2many_list_row_add a:visible",
                        extra_trigger: ".o_form_view",
                        run: function () {
                            // Assertion only; do not trigger the default
                            // click action -- see the note above.
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

                    // ── Flow 4 — On the Signer Templates tab, the existing
                    // signer line from setUpClass is only proven visible.
                    // Opening it would reopen the same Partner Python Code
                    // (widget="ace") dialog the create tour above approaches
                    // without completing, for the same ace.js lazy-load
                    // reason (see the note there) -- editing that dialog's
                    // fields is therefore left out of this tour too.
                    {
                        content: "Open the Signer Templates tab",
                        trigger: ".o_notebook .nav-link:contains(Signer Templates)",
                    },
                    {
                        content: "Existing signer template line is visible",
                        trigger:
                            ".o_field_x2many[name='signer_template_ids'] .o_data_row",
                        run: function () {
                            // Assertion only; do not open the row -- see the
                            // note above.
                        },
                    },

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
                        timeout: 20000,
                    },
                    {
                        content: "Click Delete",
                        // The Action menu items are Owl components; match the
                        // EXACT label instead of :contains(Delete), which
                        // could pick a different item as a substring
                        // (odoo-development-ui-test patterns.md §I).
                        trigger: ".o_cp_action_menus .o_menu_item a",
                        timeout: 20000,
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
                        timeout: 20000,
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
                        timeout: 20000,
                    },
                    {
                        content: "Click Archive",
                        trigger: ".o_cp_action_menus .o_menu_item a",
                        timeout: 20000,
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
                        timeout: 20000,
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
                        timeout: 20000,
                        run: function () {
                            this.$anchor[0].click();
                        },
                    },
                    {
                        // Raised timeout: this exact step failed on the OCB CI
                        // job on PR #21 (runs 31767181081 and 31768379014)
                        // while staying green on the Odoo job and in
                        // documenso_backend_tour.js's own copy of this step --
                        // see the TIMEOUT NOTE above
                        // openDocumensoSigningTemplateList().
                        content: "Enable the Archived filter",
                        trigger: ".o_filter_menu .o_menu_item a:contains(Archived)",
                        timeout: 20000,
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
                        timeout: 20000,
                    },
                    {
                        content: "Click Unarchive",
                        trigger: ".o_cp_action_menus .o_menu_item a",
                        timeout: 20000,
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
