from odoo import api, models

from .sync_metadata import mark_create_values, mark_write_values, metadata_fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    locals().update(metadata_fields())

    @api.model_create_multi
    def create(self, values_list):
        return super().create(mark_create_values(self.env, values_list))

    def write(self, values):
        return super().write(mark_write_values(self, values))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    locals().update(metadata_fields())

    @api.model_create_multi
    def create(self, values_list):
        return super().create(mark_create_values(self.env, values_list))

    def write(self, values):
        return super().write(mark_write_values(self, values))
