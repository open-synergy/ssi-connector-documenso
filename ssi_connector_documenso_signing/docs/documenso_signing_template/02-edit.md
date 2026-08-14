# Edit Documenso Signing Template

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signing.template`\
> **Menu:** Connector > Documenso > Signing > Signing Templates\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Requires:** `01-create`\
> **Inline Actions:** `action_generate_code` (Generate Code)

## Pre-Condition

- **Record:** The record to edit already exists.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Signing > Signing Templates** menu.
2. Find and open the record to edit.
3. Change the fields as needed:
   - **Name**, **Code** (or click **Generate Code** in the header — see `01-create`),
     **Source Model**, **Py3o Report**.
   - Changing **Source Model** clears the previously selected **Py3o Report**, since the
     list of allowed reports depends on **Source Model**; pick a report again afterward
     if one is needed.
4. On the **Signer Templates** tab, add, edit, or remove signer lines as needed — filled
   in the same way as `01-create`.
5. Click **Save**.

## Post-Condition

- The record is updated with the new values.
