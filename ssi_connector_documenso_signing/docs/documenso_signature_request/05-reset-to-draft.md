# Reset to Draft — Documenso Signature Request

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signature.request`\
> **Menu:** Connector > Documenso > Signing > Signature Requests\
> **Actor:** user in group `Signature Request User` (`documenso_signature_request_user_group`)\
> **State:** `cancelled` → `draft`\
> **Requires:** `04-cancel`

## Pre-Condition

- **Record:** Status is **Cancelled**.
- **Access:** User is in group `Signature Request User`.

## Flow

1. Open the **Connector > Documenso > Signing > Signature Requests** menu.
2. Open the cancelled record to reset.
3. Click the **Reset to Draft** button (`action_reset_to_draft`).

## Post-Condition

- Status returns to **Draft**.
- **Documenso Document ID**, **Signed PDF**, and **Signed PDF Filename** are cleared.
  The **Generated PDF** (if any) is kept, so **Send to Documenso** would reuse it unless
  **Generate PDF** is clicked again first.
