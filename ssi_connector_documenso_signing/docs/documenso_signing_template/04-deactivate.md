# Deactivate Documenso Signing Template

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signing.template`\
> **Menu:** Connector > Documenso > Signing > Signing Templates\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Active:** `true` → `false`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The record is currently active.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Signing > Signing Templates** menu.
2. Select one or more records to deactivate (check the checkbox).
3. Click **Action** > **Archive**.
4. Click **OK** to confirm.

## Post-Condition

- The records are archived and no longer appear in the default list view.
- The template can no longer be selected when creating a new signature request, but
  signature requests already created from it can still be viewed.
