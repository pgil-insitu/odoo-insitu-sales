from odoo import fields, models


class InsituSyncLog(models.Model):
    _name = "insitu.sync.log"
    _description = "inSitu Sales Synchronization Log"
    _order = "finished_at desc, id desc"

    profile_id = fields.Many2one(
        "insitu.connector.profile",
        required=True,
        index=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        ondelete="cascade",
    )
    entity = fields.Selection(
        [
            ("customers", "Customers"),
            ("products", "Products"),
            ("inventory", "Inventory"),
            ("orders", "Orders"),
            ("invoices", "Invoices"),
            ("payments", "Payments"),
            ("pricing", "Pricing"),
            ("warehouses", "Warehouses"),
            ("estimates", "Estimates"),
            ("taxes", "Taxes"),
            ("sales_terms", "Sales Terms"),
            ("sales_reps", "Sales Representatives"),
            ("payment_methods", "Payment Methods"),
            ("full", "Full Sync"),
        ],
        required=True,
        index=True,
    )
    direction = fields.Selection(
        [
            ("to_odoo", "inSitu to Odoo"),
            ("from_odoo", "Odoo to inSitu"),
            ("bidirectional", "Bidirectional"),
        ],
        required=True,
        index=True,
    )
    status = fields.Selection(
        [
            ("success", "Successful"),
            ("warning", "Warning"),
            ("failed", "Failed"),
        ],
        required=True,
        index=True,
    )
    processed_count = fields.Integer(default=0)
    error_count = fields.Integer(default=0)
    message = fields.Text()
    started_at = fields.Datetime(index=True)
    finished_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
