# Odoo external API protocol audit and roadmap

## Audit result — 2026-08-16

The Marketplace module contains no transport implementation. A read-only review
of the inSitu backend checkout found that the active Odoo service imports
`odoo-await`, constructs an Odoo client with URL, database, username, and
password or API key, calls `connect()`, and uses methods including `searchRead`,
`read`, `create`, `update`, and `execute_kw`.

The latest fetched backend `origin/develop` revision reviewed for this audit was
`48d7606deefa` on 2026-08-16. It still imports `odoo-await`, declares
`odoo-await` `^3.3.0`, constructs the same client, and calls `execute_kw`.
That remote branch does not track a dependency lockfile. The older local
checkout's lock resolved `odoo-await` 3.4.1 to `xmlrpc` 1.3.2, but the exact
dependency resolved by the deployed artifact must be verified independently.
The active integration path should therefore be treated as legacy XML-RPC until
deployment evidence proves otherwise.

## Risk

Odoo 19 introduces the External JSON-2 API. Odoo's 19.0 documentation schedules
the legacy XML-RPC and JSON-RPC endpoints for removal in Odoo 22 and Odoo Online
21.1. This is not an immediate Odoo 16–19 outage, but it requires a migration
before those target releases.

## Migration plan

1. Pin and lock the Odoo transport dependency, then confirm the dependency and
   endpoint behavior in the deployed backend build.
2. Inventory every Odoo model, method, context, company filter, pagination path,
   and custom action used by the current service.
3. Build a transport interface so legacy XML-RPC and JSON-2 clients can share
   mapping and business logic.
4. Add contract tests for authentication, field discovery, search/read,
   create/update, order lines, stock picking actions, payments, pagination,
   multi-company context, and error normalization.
5. Run read-only dual-transport comparisons against an Odoo 19 sandbox.
6. Enable JSON-2 writes in a sandbox and verify persisted Odoo and inSitu data.
7. Roll out per tenant behind an explicit feature flag with rollback to the
   legacy transport while supported.
8. Keep XML-RPC for Odoo releases that do not provide the required JSON-2
   behavior, then retire it only after the supported-version matrix permits.

## Release gate

Do not replace the production transport based only on library-level unit tests.
Migration requires sandbox validation of representative DSD, presales, B2B,
inventory, pricing, order, invoice, payment, and multi-company workflows plus a
controlled tenant pilot and rollback plan.
