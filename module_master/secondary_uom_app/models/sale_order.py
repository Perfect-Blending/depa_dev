# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round as round
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    secondary_uom_id = fields.Many2one('uom.uom', compute='_quantity_secondary_compute', string="Secondary UOM", store=True)
    secondary_quantity = fields.Float('Secondary Qty', compute='_quantity_secondary_compute', digits=dp.get_precision('Product Unit of Measure'), store=True)

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _quantity_secondary_compute(self):
        for order in self:
            if order.product_id.is_secondary_uom:
                uom_quantity = order.product_id.uom_id._compute_quantity(order.product_uom_qty, order.product_id.secondary_uom_id, rounding_method='HALF-UP')
                order.secondary_uom_id = order.product_id.secondary_uom_id
                order.secondary_quantity = uom_quantity

    # pass uom and qty in invoice line
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty=qty)
        if res:
            res.update({'secondary_uom_id':self.secondary_uom_id.id, 'secondary_quantity':self.secondary_quantity})
        return res
