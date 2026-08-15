inSitu Sales Connector
======================

Purpose
-------

This addon prepares Odoo 16 and later supported releases for the inSitu Sales
integration. inSitu Sales is
operational software for wholesale distributors; it does not sell the
distributor's products. The integration connects Odoo customers, products,
pricing, inventory, warehouses, orders, invoices, and payments with authorized
inSitu workflows.

Architecture
------------

The authenticated inSitu service initiates synchronization through Odoo's
remote API. Odoo remains the ERP system of record. This addon intentionally does
not store an inSitu password, run a second synchronization engine, or publish an
unauthenticated HTTP endpoint.

Supported deployment modes
--------------------------

The inSitu Sales integration supports Odoo 16, 17, 18, and 19 across these
deployment modes:

* **Odoo Online SaaS:** inSitu Sales connects through Odoo's external API. The
  Python addon is not installed on the Odoo Online database. Odoo Online
  external API access requires an Odoo Custom plan.
* **Odoo.sh and on-premise:** install the branch of this addon that matches the
  Odoo major version, then connect inSitu Sales through the external API.

The Odoo Apps availability indicator refers to whether this Python addon can be
installed on a hosting platform. It does not indicate whether the external
inSitu Sales integration supports that platform.

Configure the integration in inSitu Sales
-----------------------------------------

#. Sign in to the **inSitu Sales website**.
#. Open **Integration > Odoo**.
#. Enter **Username** for a dedicated Odoo integration user.
#. Enter the user's **Password** or, preferably, an Odoo API key.
#. Enter the Odoo instance **URL**, for example
   ``https://mycompany.odoo.com``.
#. Enter the technical **Database Name**.
#. Save the authentication settings to load the available company list.
#. Select **Company**, then save and validate the integration.

Use a dedicated integration user with only the permissions required for the
data being synchronized. Treat the API key like a password and enter it only in
the secure integration form.

Optional addon setup for Odoo.sh and on-premise
-----------------------------------------------

#. Install the branch matching your Odoo major release on Odoo.sh or an
   on-premise Odoo database.
#. Create a dedicated internal Odoo user for the integration.
#. Give the user the ``inSitu Sales / Integration Service`` role.
#. Grant Contact Creation and only the standard Odoo Sales, Inventory, and
   Accounting permissions required for the entities enabled in your inSitu
   integration.
#. Open ``inSitu Sales > Configuration > Connector Profiles``.
#. Create one profile for each participating Odoo company and choose the
   dedicated user.
#. Select ``Validate Setup``.
#. Complete **Integration > Odoo** in the inSitu Sales website using the
   connection steps above.

Do not paste API keys into profile notes, sync logs, email, or support tickets.

RPC integration reference
-------------------------

The model ``insitu.connector.profile`` exposes two authenticated model methods.

``get_connector_info()``
  Returns non-secret readiness data for the active Odoo company.

``report_sync_result(payload)``
  Persists one synchronization result. The authenticated user must have the
  Integration Service role and must match the user selected on the company
  profile (unless the caller is a connector administrator).

Example payload::

    {
        "entity": "orders",
        "direction": "to_odoo",
        "status": "success",
        "processed_count": 42,
        "error_count": 0,
        "message": "Orders synchronized",
        "started_at": "2026-08-14 12:00:00",
        "finished_at": "2026-08-14 12:00:04"
    }

Allowed entities are ``customers``, ``products``, ``inventory``, ``orders``,
``estimates``, ``invoices``, ``payments``, ``pricing``, ``warehouses``,
``taxes``, ``sales_terms``, ``sales_reps``, ``payment_methods``, and ``full``.
Allowed directions are ``to_odoo``, ``from_odoo``, and ``bidirectional``.
Allowed statuses are ``success``, ``warning``, and ``failed``.

Data retention
--------------

A daily scheduled action removes successful synchronization logs after the
configured retention period. Warning and failed logs are retained for diagnosis.

Security and multi-company behavior
-----------------------------------

Connector profiles and synchronization logs are isolated by Odoo's active
companies. The addon adds no public routes. It never persists API keys. Normal
Odoo model access still governs customers, products, orders, invoices, and
inventory records.
