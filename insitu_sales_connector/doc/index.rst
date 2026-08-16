inSitu Sales Connector
======================

Purpose
-------

The inSitu Sales integration supports Odoo 16 and later supported releases
through the external API configuration in the inSitu Sales website. The Odoo
Marketplace app is a Python-free data module that launches the inSitu Sales
application and official integration guide. It does not create a separate
integration path or synchronization engine.

inSitu Sales is operational software for wholesale distributors. The external
integration connects Odoo customers, products, pricing, inventory, warehouses,
orders, invoices, and payments with authorized inSitu workflows for DSD,
presales, offline field selling, and B2B ecommerce.

Architecture
------------

The authenticated inSitu service initiates synchronization through Odoo's
remote API. Odoo remains the ERP system of record. The Marketplace app contains
no runtime Python code, stores no credentials, and publishes no unauthenticated
endpoint. Its Odoo menu opens ``https://app.insitusales.com/`` in a new tab.

Supported connection requirement
--------------------------------

The only supported connection method for Odoo 16, 17, 18, and 19 is to enter
and validate the required Odoo parameters in the inSitu Sales website.

Odoo Online SaaS, Odoo.sh, and on-premise environments are supported only when
they provide the required external API access and all parameters below can be
entered successfully. Odoo Online external API access requires an Odoo Custom
plan. Hosting type or Marketplace app installation does not by itself establish
integration support.

Configure the integration in inSitu Sales
-----------------------------------------

#. Sign in at ``https://app.insitusales.com/``.
#. Open **Integration > Odoo**.
#. Enter **Username** for a dedicated Odoo integration user.
#. Enter the user's **Password** or, preferably, an Odoo API key.
#. Enter the Odoo instance **URL**, for example
   ``https://mycompany.odoo.com``.
#. Enter the technical **Database Name**.
#. Save the authentication settings to load the available company list.
#. Select **Company**, then save and validate the integration.

This is the **only supported integration method**. The Odoo environment is
unsupported if the customer cannot provide these parameters, the company list
cannot be loaded, or the connection cannot be validated through Odoo's external
API.

Use a dedicated integration user with only the Sales, Inventory, Accounting,
and contact permissions required for the data being synchronized. Treat the API
key like a password and enter it only in the secure integration form.

Troubleshooting connection validation
-------------------------------------

If the company list does not load or connection validation fails:

#. Confirm the URL uses HTTPS and opens the intended Odoo instance.
#. Confirm **Database Name** is the technical database name, not a company name.
#. Confirm the integration user is active and has access to the selected company.
#. Confirm the password or API key is current and has not been revoked or expired.
#. Save the authentication settings before loading the company list.
#. Stop and email support if validation still fails. Do not substitute another
   database, company, or user merely to make the test pass.

Marketplace app behavior
------------------------

The installed app adds an **inSitu Sales** entry to the Odoo app launcher with
two actions:

Selecting the top-level **inSitu Sales** app opens the authenticated inSitu
Sales application in a new tab.

``Open inSitu Sales``
  Opens the authenticated inSitu Sales application in a new tab.

``Odoo Integration Guide``
  Opens the official inSitu Sales Odoo integration page in a new tab.

The app is an Odoo Online-compatible importable/data module. It does not add
custom Odoo models, scheduled actions, security groups, synchronization logs,
or API-key storage. Synchronization begins only after the required parameters
are configured and validated in **Integration > Odoo**.

Data and permissions
--------------------

The external connector can synchronize customers, products, inventory,
warehouses, pricing, orders, invoices, payments, taxes, sales terms, sales reps,
and payment methods according to the enabled inSitu workflows and the access
rights of the dedicated Odoo integration user. Normal Odoo record rules and
multi-company access continue to govern all data returned by the external API.

Credentials and data handling
-----------------------------

The installed Odoo Marketplace module contains no runtime synchronization code,
stores no credentials, and collects no telemetry. Connection settings are
entered in the authenticated inSitu Sales integration form and are used by the
external inSitu service to access only the configured Odoo environment.

The external integration can read or write only the objects permitted by the
dedicated Odoo user's access rights and enabled inSitu workflows. Disable the
integration user or revoke its API key to stop future external API access.

Use a unique integration user rather than a personal administrator account.
Review its company access and permissions periodically, rotate credentials
according to the customer's security policy, and revoke credentials immediately
if compromise is suspected.

Support
-------

Email integration support at ``support@insitusales.com``. The Odoo Apps
**You bought this module and need support?** link is generated by Odoo and opens
Odoo's support-request screen. Odoo routes those requests to the support email
declared in the module manifest.
