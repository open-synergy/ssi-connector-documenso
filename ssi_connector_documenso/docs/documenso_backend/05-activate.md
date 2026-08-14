# Activate Documenso Backend

> **Module:** ssi_connector_documenso\
> **Model:** `documenso.backend`\
> **Menu:** Connector > Documenso > Documenso Configuration > Backends\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Active:** `false` → `true`\
> **Requires:** `04-deactivate`

## Pre-Condition

- **Record:** The record is currently archived.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Documenso Configuration > Backends** menu.
2. Enable the **Archived** filter in the search bar.
3. Select one or more records to reactivate (check the checkbox).
4. Click **Action** > **Unarchive**.

## Post-Condition

- The records are restored and appear again in the default list view.
- Other modules can select this backend again for new operations.
