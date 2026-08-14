# Check Status — Documenso Signature Request

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signature.request`\
> **Menu:** Connector > Documenso > Signing > Signature Requests\
> **Actor:** user in group `Signature Request User` (`documenso_signature_request_user_group`)\
> **State:** `sent` → `signed`\
> **Requires:** `02-send-to-documenso`

## Pre-Condition

- **Record:** Status is **Sent**.
- **Access:** User is in group `Signature Request User`.

## Flow

1. Open the **Connector > Documenso > Signing > Signature Requests** menu.
2. Open the record whose status to check.
3. Click the **Check Status** button (`action_check_status`).

## Post-Condition

- If all signers have completed signing, status changes to **Signed**, the signed PDF is
  downloaded and attached to the record (**Signed PDF** field), and a success
  notification "All signers have completed signing. The signed PDF has been downloaded."
  is shown.
- If signing is not yet complete, status remains **Sent** and a warning notification
  showing the current Documenso status is shown.

> This action calls the Documenso service over the network. The automated UI test for
> this model only covers `01-create` (see `odoo-development-ui-test`); it does not
> exercise this button beyond confirming it is visible and enabled while in the states
> above, since a tour cannot depend on an external network call completing.
