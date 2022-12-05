# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	def _prepare_invoice_line_from_po_line(self, line):
		res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
		if line.product_id.is_secondary_uom:
			quantity = res.get('quantity')
			uom_quantity = line.product_id.uom_id._compute_quantity(quantity, line.secondary_uom_id, rounding_method='HALF-UP')
			res.update({'secondary_uom_id':line.secondary_uom_id.id, 'secondary_quantity':uom_quantity})
		return res

class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	secondary_uom_id = fields.Many2one('uom.uom', compute='_quantity_secondary_compute', string="Secondary UOM", store=True)
	secondary_quantity = fields.Float('Secondary Qty', compute='_quantity_secondary_compute', digits=dp.get_precision('Product Unit of Measure'), store=True)

	@api.depends('product_id', 'quantity', 'uom_id')
	def _quantity_secondary_compute(self):
		for order in self:
			if order.product_id.is_secondary_uom:
				uom_quantity = order.product_id.uom_id._compute_quantity(order.quantity, order.product_id.secondary_uom_id, rounding_method='HALF-UP')
				order.secondary_uom_id = order.product_id.secondary_uom_id
				order.secondary_quantity = uom_quantity
