# Cancel Documenso Signature Request

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signature.request`\
> **Menu:** Connector > Documenso > Signing > Signature Requests\
> **Actor:** user in group `Signature Request User` (`documenso_signature_request_user_group`)\
> **State:** `draft` | `sent` → `cancelled`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft** or **Sent**.
- **Access:** User is in group `Signature Request User`.

## Flow

1. Open the **Connector > Documenso > Signing > Signature Requests** menu.
2. Open the record to cancel.
3. Click the **Cancel** button (`action_cancel`).

## Post-Condition

- Status changes to **Cancelled**.
