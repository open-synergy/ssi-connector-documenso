# Delete Documenso Backend

> **Module:** ssi_connector_documenso\
> **Model:** `documenso.backend`\
> **Menu:** Connector > Documenso > Documenso Configuration > Backends\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The record is not referenced by other data that requires this backend
  (e.g. pending signing bindings).
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Documenso Configuration > Backends** menu.
2. Select one or more records to delete (check the checkbox).
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The selected records are permanently removed from the system.
