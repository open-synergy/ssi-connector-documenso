# Create Documenso Signing Template

> **Module:** ssi_connector_documenso_signing\
> **Model:** `documenso.signing.template`\
> **Menu:** Connector > Documenso > Signing > Signing Templates\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Inline Actions:** `action_generate_code` (Generate Code)

## Pre-Condition

- **Config:** An active `sequence.template` for this model exists — only needed when
  using **Generate Code** instead of typing a code manually.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Signing > Signing Templates** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the fields:
   - **Name** _(required)_: Enter a name that identifies this signing template.
   - **Code** _(required)_: Enter a unique code, or leave it as **/** and click
     **Generate Code** in the header to auto-assign one from the configured sequence
     template. **Generate Code** only replaces a code that is still **/**, and fails
     with an error if no sequence template is configured for this model.
4. On the **Document** tab, fill in:
   - **Source Model** _(required)_: Enter the technical name of the Odoo model this
     template applies to (e.g. `sale.order`, `account.move`).
   - **Py3o Report**: Select the py3o report used to generate the PDF. Only py3o PDF
     reports registered for **Source Model** are listed, and the list is empty until
     **Source Model** is filled in.
5. On the **Signer Templates** tab, add one or more signer lines. Repeat the following
   steps as many times as needed to add a line:
   - Click **Add a line**.
   - Fill in the line with:
     - **Role**: Defaults to **Signer**. Change to **CC**, **Approver**, or **Viewer**
       if needed.
     - **Signing Order**: Defaults to **1**. Use the same number for signers who sign in
       parallel; use different numbers to enforce an order.
     - **Signature Anchor**: Enter the placeholder text used in the py3o template to
       position this signer's signature field (e.g. `{{SIGN_1}}`).
     - **Signature Width (%)** / **Signature Height (%)**: Optional custom size of the
       signature field. Leave at 0 to use the default minimum size.
     - **Partner Python Code** _(required)_: Enter a Python expression that resolves to
       the `res.partner` who signs, evaluated against the source document when the
       template is applied to a signature request.
6. Click **Save**.

## Post-Condition

- A new **Documenso Signing Template** record is created and appears in the Signing
  Templates list.
- The record is active by default, so it can be selected when creating a signature
  request for the matching **Source Model**.
