# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class StockQuant(models.Model):
	_inherit = 'stock.quant'

	secondary_uom_id = fields.Many2one('uom.uom', compute='_quantity_secondary_compute', string="Secondary UOM", store=True)
	secondary_quantity = fields.Float('Secondary Qty', compute='_quantity_secondary_compute', digits=dp.get_precision('Product Unit of Measure'), store=True)

	@api.depends('product_id', 'quantity', 'product_uom_id')
	def _quantity_secondary_compute(self):
		for quant in self:
			if quant.product_id.is_secondary_uom:
				uom_quantity = quant.product_id.uom_id._compute_quantity(quant.quantity, quant.product_id.secondary_uom_id, rounding_method='HALF-UP')
				quant.secondary_uom_id = quant.product_id.secondary_uom_id
				quant.secondary_quantity = uom_quantity

