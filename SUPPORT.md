# Support and version lifecycle

## Supported releases

The actively maintained Marketplace branches are:

| Odoo release | Branch | Status |
| --- | --- | --- |
| 19.0 | `19.0` and `main` | Supported |
| 18.0 | `18.0` | Supported |
| 17.0 | `17.0` | Supported |
| 16.0 | `16.0` | Supported |

Support requires a successful connection through **Integration > Odoo** in the
inSitu Sales website. Odoo Online, Odoo.sh, and on-premise are supported only
when all required parameters can be entered and validated. Odoo Online external
API access requires a Custom plan.

## What support covers

- Installing or importing the matching Marketplace data module.
- Configuring and validating the supported external API connection.
- Diagnosing company-list, authentication, permission, and synchronization
  failures for supported workflows.
- Correcting defects in the Marketplace package or supported inSitu integration.

Support does not include an alternative connection method when the required
parameters or external API access are unavailable.

## Release retirement

A release remains supported while its branch and Marketplace entry are marked
Supported above. Before retiring a major version, inSitu Sales will update this
file and the changelog and will stop describing that version as actively
supported in the Marketplace listing. Existing integrations should be upgraded
to a maintained Odoo release before retirement.

## Contact

Email `support@insitusales.com` with the Odoo version, hosting type, database URL
without credentials, company name, validation error, and approximate timestamp.
Never send passwords or API keys by email.
