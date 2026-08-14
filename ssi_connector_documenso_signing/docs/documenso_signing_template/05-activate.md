# Activate Documenso Signing Template

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signing.template`\
> **Menu:** Connector > Documenso > Signing > Signing Templates\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Active:** `false` → `true`\
> **Requires:** `04-deactivate`

## Pre-Condition

- **Record:** The record is currently archived.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Signing > Signing Templates** menu.
2. Enable the **Archived** filter in the search bar.
3. Select one or more records to reactivate (check the checkbox).
4. Click **Action** > **Unarchive**.

## Post-Condition

- The records are restored and appear again in the default list view.
- The template can be selected again when creating a new signature request.
