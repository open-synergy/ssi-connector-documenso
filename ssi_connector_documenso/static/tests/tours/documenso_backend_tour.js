// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_connector_documenso.documenso_backend_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared navigation block reused by every tour below -- it corresponds to
    // Flow 1 of every documenso_backend IK: "Open the Connector > Documenso >
    // Documenso Configuration > Backends menu."
    //
    // The IK menu path has four levels but only three are clickable. "Connector"
    // is the app icon. "Documenso" (menu_documenso_root) is a direct child of the
    // app root menu, so it is always rendered as its own top-nav dropdown
    // section, even though it carries no action of its own. "Documenso
    // Configuration" (menu_documenso_configuration) is one level deeper, has no
    // action, and does have a child ("Backends") -- 14.0 therefore renders it as
    // a .dropdown-header with no data-menu-xmlid, and flattens "Backends" into
    // the same "Documenso" dropdown (odoo-development-ui-test patterns.md §A,
    // same mechanic as the "Virtual Account" level in ssi_va/va_biller_tour.js).
    function openDocumensoBackendList() {
        return [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Connector app",
                trigger: '.o_app[data-menu-xmlid="ssi_connector.menu_root_connector"]',
            },
            {
                content: "Open the Documenso menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso.menu_documenso_root"]',
            },
            {
                content: "Open the Backends menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_connector_documenso.menu_documenso_backend"]',
            },
            {
                // Gate: wait for the TARGET action to be installed, not just for
                // "a list is on screen". Opening an app lands on its first menu
                // action, which is also a .o_list_view -- using that as a gate
                // would let the next steps act on the wrong view
                // (odoo-development-ui-test patterns.md §A).
                content: "Documenso Backends list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Documenso Backends)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ];
    }

    // IK: docs/documenso_backend/01-create.md
    tour.register(
        "ssi_connector_documenso_documenso_backend_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Connector > Documenso > Documenso
            // Configuration > Backends menu.
            openDocumensoBackendList(),
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
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },

                // ── Flow 3 — Fill in the fields (Name, Base URL, API Key,
                // API Version). Company keeps its default and is not touched.
                {
                    content: "Fill in Name",
                    trigger: ".o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR DOCUMENSO BACKEND Create",
                },
                {
                    content: "Fill in Base URL",
                    trigger: ".o_field_widget[name='base_url']",
                    run: "text https://example.com",
                },
                {
                    content: "Fill in API Key",
                    trigger: ".o_field_widget[name='api_key']",
                    run: "text TOUR-DUMMY-API-KEY",
                },
                {
                    // API Version already defaults to "API v2" -- this step
                    // only confirms the field is present and rendered, per the
                    // IK ("Defaults to API v2. Change to API v1 ..."); the
                    // selected value itself is not asserted here.
                    content: "API Version field is present",
                    trigger: ".o_field_widget[name='version']",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },

                // ── Flow 4 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // ── Post-Condition — A new Documenso Backend record is
                // created and appears in the Backends list, active by
                // default. Only what is visible is asserted here: that the
                // record is saved and displayed.
                {
                    content: "Record is saved and displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(TOUR DOCUMENSO BACKEND Create)",
                    extra_trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ]
        )
    );

    // IK: docs/documenso_backend/02-edit.md
    tour.register(
        "ssi_connector_documenso_documenso_backend_edit",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Backends menu.
            openDocumensoBackendList(),
            [
                // ── Flow 2 — Find and open the record to edit.
                {
                    content: "Open the backend record",
                    trigger:
                        ".o_data_row:contains(TOUR DOCUMENSO BACKEND Edit) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
                {
                    // 14.0 opens an existing record read-only, so the Edit
                    // button must be clicked before any field can be touched
                    // (odoo-development-ui-test patterns.md §E). This is a
                    // version mechanic of the 14.0 web client, not an extra
                    // Flow step: from 17.0 on the form is always editable.
                    content: "Click the Edit button",
                    trigger: ".o_form_button_edit",
                },
                {
                    content: "Form is now editable",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },

                // ── Flow 3 — Change the fields.
                {
                    content: "Change the Name",
                    trigger: ".o_field_widget[name='name']",
                    run: "text TOUR DOCUMENSO BACKEND Edit Changed",
                },

                // ── Flow 4 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // ── Post-Condition — The record is updated with the new
                // values. The stored value itself is unit test territory;
                // only that the form returns to readonly, saved state is
                // asserted here.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ]
        )
    );

    // IK: docs/documenso_backend/03-delete.md
    tour.register(
        "ssi_connector_documenso_documenso_backend_delete",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Backends menu.
            openDocumensoBackendList(),
            [
                // ── Flow 2 — Select the record to delete (checkbox).
                {
                    content: "Select the record to delete",
                    trigger:
                        ".o_data_row:contains(TOUR DOCUMENSO BACKEND Delete) " +
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
                    // EXACT label instead of :contains(Delete), which could
                    // pick a different item as a substring
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
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR DOCUMENSO BACKEND Delete)))",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ]
        )
    );

    // IK: docs/documenso_backend/04-deactivate.md
    tour.register(
        "ssi_connector_documenso_documenso_backend_deactivate",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Backends menu.
            openDocumensoBackendList(),
            [
                // ── Flow 2 — Select the record to deactivate (checkbox).
                {
                    content: "Select the record to deactivate",
                    trigger:
                        ".o_data_row:contains(TOUR DOCUMENSO BACKEND Deactivate) " +
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
                        var $archive = $(".o_cp_action_menus .o_menu_item a").filter(
                            function () {
                                return $(this).text().trim() === "Archive";
                            }
                        );
                        $archive[0].click();
                    },
                },

                // ── Flow 4 — Click OK to confirm.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // ── Post-Condition — The record is archived and no longer
                // appears in the default list view. Whether other modules can
                // still select this backend is not a visible fact of this
                // screen and belongs to the unit tests.
                {
                    content: "Record no longer appears in the active list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR DOCUMENSO BACKEND Deactivate)))",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ]
        )
    );

    // IK: docs/documenso_backend/05-activate.md
    tour.register(
        "ssi_connector_documenso_documenso_backend_activate",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Backends menu.
            openDocumensoBackendList(),
            [
                // ── Flow 2 — Enable the Archived filter in the search bar.
                {
                    content: "Open the Filters menu",
                    // 14.0: the Filters dropdown is an Owl component whose
                    // open state does not always flip on the synthetic mouse
                    // event sequence -- use a real browser click
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
                        ".o_data_row:contains(TOUR DOCUMENSO BACKEND Activate) " +
                        ".o_list_record_selector input",
                    run: "click",
                },

                // ── Flow 4 — Click Action > Unarchive. There is no step for
                // a confirm dialog: 14.0 shows no dialog for Unarchive (see
                // web/static/src/js/views/list/list_controller.js
                // _getActionMenuItems -- only "Archive" wraps its callback in
                // Dialog.confirm(...), while "Unarchive" calls
                // _toggleArchiveState(false) directly), which is why the IK
                // itself has no confirm step for this action.
                {
                    content: "Open the Action menu",
                    trigger: ".o_cp_action_menus button:contains(Action)",
                },
                {
                    content: "Click Unarchive",
                    trigger: ".o_cp_action_menus .o_menu_item a",
                    run: function () {
                        var $unarchive = $(".o_cp_action_menus .o_menu_item a").filter(
                            function () {
                                return $(this).text().trim() === "Unarchive";
                            }
                        );
                        $unarchive[0].click();
                    },
                },

                // ── Post-Condition — The record is restored and belongs to
                // the default (active) list again. With the Archived filter
                // still on -- turning it off is not a step of this IK -- the
                // visible proof is that the row leaves the archived-only
                // list, which can only happen once its Active flag is back to
                // true.
                {
                    content: "Record leaves the archived list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR DOCUMENSO BACKEND Activate)))",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ]
        )
    );

    // IK: docs/documenso_backend/06-test-connection.md
    tour.register(
        "ssi_connector_documenso_documenso_backend_test_connection",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Backends menu.
            openDocumensoBackendList(),
            [
                // ── Flow 2 — Open the record to test.
                {
                    content: "Open the backend record",
                    trigger:
                        ".o_data_row:contains(TOUR DOCUMENSO BACKEND Test Connection) " +
                        ".o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },

                // ── Flow 3 — Click the Test Connection button in the header.
                // The record's base_url (http://127.0.0.1:1, set in
                // setUpClass) refuses the connection immediately, so
                // action_test_connection always raises NetworkRetryableError
                // instead of returning the success notification -- this is
                // deliberate: the tour must not depend on outbound network
                // access, per the IK ("does not call Documenso for real").
                {
                    content: "Click Test Connection",
                    trigger:
                        ".o_statusbar_buttons button[name='action_test_connection']",
                    extra_trigger: ".o_form_view",
                },

                // ── Post-Condition — A message is shown reporting that the
                // connection failed. An uncaught exception raised by a
                // button's server-side call is rendered by 14.0's
                // CrashManager as a dialog carrying the "o_dialog_error"
                // class (odoo/addons/web/static/src/xml/crash_manager.xml,
                // template "CrashManager.error") -- that is the visible,
                // user-facing message this step waits for. Its text content
                // is not asserted; that belongs to the unit tests.
                {
                    content: "A connection failure message is shown",
                    trigger: ".o_dialog_error",
                    run: function () {
                        // Assertion only; do not trigger the default click
                        // action.
                    },
                },
            ]
        )
    );
});
