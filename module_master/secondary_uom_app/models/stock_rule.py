# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if res:
            if values.get('sale_line_id'):
                sale_line_id = self.env['sale.order.line'].browse(values.get('sale_line_id'))
                if sale_line_id:
                    res.update({
                        'secondary_uom_id': sale_line_id.secondary_uom_id and sale_line_id.secondary_uom_id.id or False,
                        'secondary_quantity': sale_line_id.secondary_quantity or 0.0
                    })
        return res