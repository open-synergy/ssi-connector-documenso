# Test Connection on Documenso Backend

> **Module:** ssi_connector_documenso\
> **Model:** `documenso.backend`\
> **Menu:** Connector > Documenso > Documenso Configuration > Backends\
> **Actor:** user in group `Connector Manager` (`connector.group_connector_manager`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A Documenso Backend record exists, with **Base URL**, **API Key**, and
  **API Version** filled in.
- **Access:** User is in group `Connector Manager`.

## Flow

1. Open the **Connector > Documenso > Documenso Configuration > Backends** menu.
2. Open the record to test.
3. Click the **Test Connection** button in the header (`action_test_connection`).

## Post-Condition

- A message is shown reporting whether the connection to the Documenso instance
  succeeded or failed.
- The record's stored values are not changed by this action.
