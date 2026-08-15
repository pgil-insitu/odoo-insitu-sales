# inSitu Sales Connector for Odoo

An Odoo 16+ integration for inSitu Sales. Odoo Online SaaS connects directly
through Odoo's external API without installing an addon. Odoo.sh and on-premise
deployments can install this addon to add an Odoo-side control surface.

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

## Supported Odoo versions and hosting

- Odoo 16, 17, 18, and 19
- Odoo Online SaaS through the external API; no addon installation is required
- Odoo.sh and on-premise installations with this connector addon
- Community and Enterprise editions where the selected deployment provides the
  required external API access

Each Odoo major release is maintained on a matching Git branch (`16.0`, `17.0`,
`18.0`, or `19.0`) with an Odoo-specific manifest and backend view definitions.

The red **Odoo Online** availability indicator on the Odoo Apps page describes
where this Python addon can be installed. It does not describe the availability
of the inSitu Sales integration. Odoo Online does not install the addon; inSitu
Sales connects to the hosted database through Odoo's external API. Odoo Online
external API access requires an Odoo Custom plan.

## Configure the integration in inSitu Sales

For Odoo Online, Odoo.sh, and on-premise deployments:

1. Sign in to the **inSitu Sales website**.
2. Open **Integration > Odoo**.
3. Enter the Odoo connection parameters:
   - **Username**: the login for a dedicated Odoo integration user.
   - **Password**: the user's Odoo password or, preferably, an Odoo API key.
   - **URL**: the Odoo instance URL, such as `https://mycompany.odoo.com`.
   - **Database Name**: the technical name of the Odoo database.
4. Save the authentication settings so inSitu Sales can load the available
   companies.
5. Select **Company**, then save and validate the integration.

Use a dedicated integration user with only the Sales, Inventory, Accounting,
and contact permissions required for the data being synchronized. Treat an API
key like a password and provide it only through the secure integration form.

## Optional addon installation for Odoo.sh and on-premise

Skip this section for Odoo Online SaaS.

1. Copy `insitu_sales_connector` into an Odoo addons path.
2. Update the Apps list.
3. Install **inSitu Sales Connector**.
4. Open **inSitu Sales > Configuration > Connector Profiles**.
5. Select a dedicated internal Odoo user and grant it Contact Creation plus the
   normal Sales, Inventory, and Accounting permissions required for the entities
   you want to synchronize, as well as the **inSitu Sales / Integration
   Service** role.
6. Select **Validate Setup**.
7. Complete **Integration > Odoo** in the inSitu Sales website using the
   connection steps above. Secrets are never displayed or persisted by this
   addon.

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
