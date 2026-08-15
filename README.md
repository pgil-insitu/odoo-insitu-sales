# inSitu Sales Connector for Odoo

An installable Odoo 16+ addon that prepares an Odoo database for the existing
inSitu Sales integration and gives administrators an Odoo-side control surface.

inSitu Sales is operational software for wholesale distributors. The connector
keeps Odoo as the ERP system of record while inSitu Sales supports field sales,
DSD, mobile invoicing, inventory visibility, and B2B ordering.

## What the addon provides

- A per-company connector profile with the exact Odoo URL, database, and login
  details needed by the inSitu integration team.
- A dedicated Odoo security role for the integration service user.
- Readiness validation before credentials are configured in inSitu Sales.
- Multi-company-safe synchronization logs and last-run status.
- Source and external-reference metadata on customers, products, sales orders,
  order lines, invoices, and stock transfers.
- RPC methods for connector health checks and persisted synchronization results.
- Automatic retention cleanup for old synchronization logs.

The addon does **not** store an inSitu password or duplicate the synchronization
engine. The inSitu service initiates synchronization through Odoo's authenticated
remote API, matching the production connector architecture.

## Supported Odoo versions

- Odoo 16, 17, 18, and 19 Community and Enterprise
- Odoo.sh and on-premise installations

Each Odoo major release is maintained on a matching Git branch (`16.0`, `17.0`,
`18.0`, or `19.0`) with an Odoo-specific manifest and backend view definitions.

Odoo Online does not allow third-party Python addons.

## Installation

1. Copy `insitu_sales_connector` into an Odoo addons path.
2. Update the Apps list.
3. Install **inSitu Sales Connector**.
4. Open **inSitu Sales > Configuration > Connector Profiles**.
5. Select a dedicated internal Odoo user and grant it Contact Creation plus the
   normal Sales, Inventory, and Accounting permissions required for the entities
   you want to synchronize, as well as the **inSitu Sales / Integration
   Service** role.
6. Select **Validate Setup** and send the displayed connection details through
   your approved support channel. Create and share the Odoo API key outside this
   addon; secrets are never displayed or persisted here.

See [doc/index.rst](insitu_sales_connector/doc/index.rst) for administrator and
integration-reference documentation.

## Local verification

Run the repository checks:

```bash
./scripts/validate.sh
```

Run an Odoo installation test with Docker:

```bash
docker compose up -d db
docker compose run --rm odoo-test
docker compose down
```

The compose file uses development-only database credentials and keeps all data
inside Docker-managed volumes.

## License

Apache License 2.0. See [LICENSE](LICENSE).
