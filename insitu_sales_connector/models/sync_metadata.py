from odoo import fields


SYNC_STATUS_SELECTION = [
    ("pending", "Pending"),
    ("success", "Successful"),
    ("warning", "Warning"),
    ("failed", "Failed"),
]


def metadata_fields():
    """Return a fresh field mapping for an Odoo business model."""
    return {
        "insitu_origin": fields.Boolean(
            string="Created by inSitu Sales",
            copy=False,
            index=True,
            help="The record was created through the inSitu Sales integration user.",
        ),
        "insitu_external_id": fields.Char(
            string="inSitu Reference",
            copy=False,
            index=True,
            help="Optional identifier of the corresponding record in inSitu Sales.",
        ),
        "insitu_last_sync_at": fields.Datetime(
            string="Last inSitu Update",
            copy=False,
            index=True,
        ),
        "insitu_sync_status": fields.Selection(
            selection=SYNC_STATUS_SELECTION,
            string="inSitu Sync Status",
            copy=False,
            index=True,
        ),
    }


def _is_assigned_integration_user(env, company_ids=None):
    if not env.user.has_group("insitu_sales_connector.group_insitu_integration"):
        return False
    company_ids = company_ids or env.companies.ids
    return bool(
        env["insitu.connector.profile"]
        .sudo()
        .search_count(
            [
                ("active", "=", True),
                ("integration_user_id", "=", env.user.id),
                ("company_id", "in", company_ids),
            ],
            limit=1,
        )
    )


def mark_create_values(env, values_list):
    company_ids = {
        values.get("company_id") or env.company.id for values in values_list
    }
    if not _is_assigned_integration_user(env, list(company_ids)):
        return values_list
    now = fields.Datetime.now()
    for values in values_list:
        values.setdefault("insitu_origin", True)
        values.setdefault("insitu_last_sync_at", now)
        values.setdefault("insitu_sync_status", "success")
    return values_list


def mark_write_values(records, values):
    company_ids = (
        records.mapped("company_id").ids
        if "company_id" in records._fields
        else records.env.companies.ids
    )
    if _is_assigned_integration_user(records.env, company_ids):
        values.setdefault("insitu_last_sync_at", fields.Datetime.now())
        values.setdefault("insitu_sync_status", "success")
    return values
