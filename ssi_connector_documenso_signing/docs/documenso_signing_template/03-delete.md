# Delete Documenso Signing Template

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signing.template`\
> **Menu:** Connector > Documenso > Signing > Signing Templates\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The record is not referenced by other data that requires this template
  (e.g. `documenso.signature.request` records created from it).
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Signing > Signing Templates** menu.
2. Select one or more records to delete (check the checkbox).
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The selected records are permanently removed from the system.
