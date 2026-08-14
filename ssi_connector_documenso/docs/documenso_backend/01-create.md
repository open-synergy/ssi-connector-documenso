# Create Documenso Backend

> **Module:** ssi_connector_documenso\
> **Model:** `documenso.backend`\
> **Menu:** Connector > Documenso > Documenso Configuration > Backends\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)

## Pre-Condition

- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Documenso Configuration > Backends** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the fields:
   - **Name** _(required)_: Enter a name that identifies this Documenso backend.
   - **Base URL** _(required)_: Enter the Documenso instance URL, e.g.
     `https://app.documenso.com`.
   - **API Key** _(required)_: Enter the API token generated from the Documenso account
     settings. The field is masked as a password so its value is not shown on screen.
   - **API Version** _(required)_: Defaults to **API v2**. Change to **API v1** if the
     Documenso instance only supports the older API.
   - **Company**: Automatically filled from the current company. Change if needed.
4. Click **Save**.

## Post-Condition

- A new **Documenso Backend** record is created and appears in the Backends list.
- The record is active by default, so it is available for use by other modules that
  connect to Documenso.
