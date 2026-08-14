# Send to Documenso — Documenso Signature Request

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signature.request`\
> **Menu:** Connector > Documenso > Signing > Signature Requests\
> **Actor:** user in group `Signature Request User` (`documenso_signature_request_user_group`)\
> **State:** `draft` → `sent`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Record:** At least one line exists in the **Signers** tab.
- **Access:** User is in group `Signature Request User`.

## Flow

1. Open the **Connector > Documenso > Signing > Signature Requests** menu.
2. Open the draft record to send.
3. Click the **Send to Documenso** button (`action_send_to_documenso`).
4. Click **OK** on the confirmation dialog.

## Post-Condition

- A notification "Document queued for sending to Documenso." is shown immediately; the
  request is generated (if not already) and uploaded to Documenso by a background job,
  not synchronously.
- Once the background job completes successfully, status changes to **Sent** and
  **Documenso Document ID** is filled with the ID returned by Documenso.
- Status remains **Draft** until the background job completes.
