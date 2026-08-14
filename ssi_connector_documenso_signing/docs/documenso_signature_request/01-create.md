# Create Documenso Signature Request

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signature.request`\
> **Menu:** Connector > Documenso > Signing > Signature Requests\
> **Actor:** user in group `Signature Request User` (`documenso_signature_request_user_group`)\
> **State:** `—` → `draft`\
> **Inline Actions:** `action_generate_pdf` (Generate PDF)

## Pre-Condition

- **Config:** An active `documenso.backend` record exists.
- **Config:** An active `documenso.signing.template` record exists for the source model
  to be used (only needed when filling the request from a template instead of manually).
- **Data:** The source document (e.g. a `sale.order` record) that will be signed already
  exists, since **Source Record ID** must reference an existing record.
- **Access:** User is in group `Signature Request User`.

## Flow

1. Open the **Connector > Documenso > Signing > Signature Requests** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the fields:
   - **Signing Template**: Select a signing template to auto-fill the **Source Model**,
     **Py3o Report**, and **Signers** below. Optional — leave empty to fill everything
     manually.
   - **Documenso Backend** _(required)_: Automatically filled with the first active
     Documenso backend. Change if needed.
   - **Source Model** _(required)_: Automatically filled from **Signing Template** if
     selected. Otherwise, enter the technical name of the source Odoo model that owns
     the document (e.g. `sale.order`, `account.move`).
   - **Source Record ID** _(required)_: Enter the ID of the source record this request
     applies to.
   - **Py3o Report** _(required)_: Automatically filled from **Signing Template** if
     both **Signing Template** and **Source Model** are set. Otherwise, select a py3o
     report matching **Source Model**.
   - **Company**: Automatically filled from the current company. Change if needed.
4. On the **Signers** tab: if **Signing Template** and **Source Record ID** are both
   set, the tab is automatically populated with signer lines from the template. Add,
   edit, or remove lines manually as needed. Repeat the following steps as many times as
   needed to add a line:
   - Click **Add a line**.
   - Fill in each line with:
     - **Signer** _(required)_: Select the contact who will sign the document.
     - **Role**: Defaults to **Signer**. Change to **CC**, **Approver**, or **Viewer**
       if needed.
     - **Signing Order**: Defaults to **1**. Use the same number for signers who sign in
       parallel; use different numbers to enforce an order.
     - **Signature Anchor**: Enter the placeholder text used in the py3o template to
       position this signer's signature field (e.g. `{{SIGN_1}}`).
     - **Signature Width (%)** / **Signature Height (%)**: Optional custom size of the
       signature field. Leave at 0 to use the default minimum size.
   - At least one signer line is required — **Generate PDF** and **Send to Documenso**
     will fail without one.
5. Click **Save**.
6. Optionally, click **Generate PDF** to generate the PDF from the selected **Py3o
   Report** and preview it before sending. This is not required to proceed — **Send to
   Documenso** (see `02-send-to-documenso`) generates the PDF automatically if it has
   not been generated yet, using the same **Py3o Report** and **Signers** already filled
   in on this form.

## Post-Condition

- A new **Documenso Signature Request** record is created with status **Draft**.
- The record appears in the Signature Requests list.
- If **Generate PDF** was clicked, the generated PDF is attached to the record and
  visible in the **Generated PDF** field.
