# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class StockMove(models.Model):
	_inherit = 'stock.move'

	secondary_uom_id = fields.Many2one('uom.uom', compute='_quantity_secondary_compute', string="Secondary UOM", store=True)
	secondary_quantity = fields.Float('Secondary Qty', compute='_quantity_secondary_compute', digits=dp.get_precision('Product Unit of Measure'), store=True)
	secondary_done_qty = fields.Float('Secondary Quantity Done', compute='_quantity_secondary_done_compute', digits=dp.get_precision('Product Unit of Measure'), inverse='_quantity_secondary_done_set')
 
	@api.depends('product_id', 'product_uom_qty', 'product_uom')
	def _quantity_secondary_compute(self):
		for order in self:
			if order.product_id.is_secondary_uom:
				uom_quantity = order.product_id.uom_id._compute_quantity(order.product_uom_qty, order.product_id.secondary_uom_id, rounding_method='HALF-UP')
				order.secondary_uom_id = order.product_id.secondary_uom_id
				order.secondary_quantity = uom_quantity

	@api.depends('move_line_ids.secondary_done_qty', 'move_line_ids.secondary_uom_id', 'move_line_nosuggest_ids.secondary_done_qty')
	def _quantity_secondary_done_compute(self):
		""" This field represents the sum of the move lines `qty_done`. It allows the user to know
		if there is still work to do.
 
		We take care of rounding this value at the general decimal precision and not the rounding
		of the move's UOM to make sure this value is really close to the real sum, because this
		field will be used in `_action_done` in order to know if the move will need a backorder or
		an extra move.
		"""
		for move in self:
			quantity_done = 0
			for move_line in move._get_move_lines():
				quantity_done += move_line.secondary_uom_id._compute_quantity(move_line.secondary_done_qty, move.secondary_uom_id, round=False)
			move.secondary_done_qty = quantity_done
 
	def _quantity_secondary_done_set(self):
		quantity_done = self[0].secondary_done_qty  # any call to create will invalidate `move.quantity_done`
		for move in self:
			move_lines = move._get_move_lines()
			if not move_lines:
				if quantity_done:
					# do not impact reservation here
					move_line = self.env['stock.move.line'].create(dict(move._prepare_move_line_vals(), qty_done=quantity_done))
					move.write({'move_line_ids': [(4, move_line.id)]})
			elif len(move_lines) == 1:
				move_lines[0].qty_done = quantity_done
			else:
				raise UserError(_("Cannot set the done quantity from this stock move, work directly with the move lines."))

	def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
		res = super(StockMove, self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
		if res:
			res.update({
				'secondary_uom_id': self.secondary_uom_id and self.secondary_uom_id.id or False,
			})
			if quantity:
				if self.product_id.is_secondary_uom:
					uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.secondary_uom_id, rounding_method='HALF-UP')
					uom_quantity_back_to_product_uom = self.secondary_uom_id._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
					rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
					if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
						res = dict(res, secondary_quantity=uom_quantity)
					else:
						res = dict(res, secondary_quantity=uom_quantity, product_uom_id=self.product_id.uom_id.id)
		return res

class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM",compute="secondary_qty_compute" ,store=True)
	secondary_quantity = fields.Float("Secondary Qty", digits=dp.get_precision('Product Unit of Measure') ,compute="secondary_qty_compute" ,store=True)
	secondary_done_qty = fields.Float("Secondary Done Qty", digits=dp.get_precision('Product Unit of Measure'))


	@api.depends('product_id','product_uom_qty','qty_done','secondary_uom_id')
	def secondary_qty_compute(self):
		for move_line in self:
			if move_line.product_id.is_secondary_uom:
				uom_quantity = move_line.product_id.uom_id._compute_quantity(move_line.product_uom_qty or move_line.qty_done, move_line.product_id.secondary_uom_id, rounding_method='HALF-UP')
				move_line.secondary_uom_id = move_line.product_id.secondary_uom_id
				move_line.secondary_quantity = uom_quantity
				uom_done_quantity = move_line.product_id.uom_id._compute_quantity(move_line.qty_done, move_line.product_id.secondary_uom_id, rounding_method='HALF-UP')
				move_line.secondary_done_qty = uom_done_quantity

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4::