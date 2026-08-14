# Deactivate Documenso Backend

> **Module:** ssi_connector_documenso\
> **Model:** `documenso.backend`\
> **Menu:** Connector > Documenso > Documenso Configuration > Backends\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Active:** `true` → `false`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The record is currently active.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Documenso Configuration > Backends** menu.
2. Select one or more records to deactivate (check the checkbox).
3. Click **Action** > **Archive**.
4. Click **OK** to confirm.

## Post-Condition

- The records are archived and no longer appear in the default list view.
- Other modules can no longer select this backend for new operations, but data that
  already references it can still be viewed.
