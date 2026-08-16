# Security and data handling

## Marketplace module boundary

The installed `insitu_sales_connector` module is a Python-free data module. It
adds launcher links, contains no synchronization runtime, stores no credentials,
publishes no endpoint, and collects no telemetry.

The external inSitu Sales service performs synchronization only after an
authorized administrator enters and validates the required Odoo connection in
**Integration > Odoo**.

## Credential practices

- Use a dedicated Odoo integration user, not a personal administrator account.
- Grant only the companies and Sales, Inventory, Accounting, and contact access
  needed by enabled workflows.
- Prefer an Odoo API key to a reusable account password.
- Treat an API key like a password; never commit it or send it by email.
- Rotate credentials according to the customer's security policy and revoke
  them immediately if exposure is suspected.
- Disable the integration user or revoke its key to stop future external access.

## Data scope

Depending on enabled workflows and Odoo permissions, synchronization can process
customers, addresses, products, pricing, inventory, warehouses, sales reps,
orders, invoices, payments, taxes, payment methods, and sales terms. Odoo record
rules and multi-company access remain authoritative for what the integration
user can access.

## Reporting a security concern

Email `support@insitusales.com` with a concise description, affected Odoo and
inSitu versions, timestamps, and reproduction steps. Do not include credentials,
API keys, customer exports, or other sensitive data in the initial message.
