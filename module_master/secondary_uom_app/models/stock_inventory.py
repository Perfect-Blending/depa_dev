# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductChangeQuantity(models.TransientModel):
	_inherit = "stock.change.product.qty"

	# update inventory line when update stock by "Update Qty On Hand" button from product.
	def _action_start_line(self):
		line_data=super(ProductChangeQuantity, self)._action_start_line()
		for rec in self:
			secondary_qty = 0.0
			if rec.product_id.secondary_uom_id.uom_type =='bigger':
				if rec.product_id.secondary_uom_id.factor_inv != 0:
					secondary_qty = line_data['product_qty']/rec.product_id.secondary_uom_id.factor_inv
			if rec.product_id.secondary_uom_id.uom_type =='smaller':
				secondary_qty = line_data['product_qty'] * rec.product_id.secondary_uom_id.factor
			line_data.update({'secondary_uom_id':rec.product_id.secondary_uom_id.id, 'secondary_quantity':secondary_qty})
		return line_data

class StockInventoryLine(models.Model):
	_inherit = 'stock.inventory.line'

	secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")
	secondary_quantity = fields.Float("Secondary Quantity", digits=(1,5))

	# get secondary uom and qty when update Inventory Adjustment by entering real qty  
	@api.onchange('product_id', 'product_qty')
	def change_product(self):
		if self.product_id:
			self.secondary_uom_id = self.product_id.secondary_uom_id
			if self.secondary_uom_id.uom_type =='bigger':
				if self.secondary_uom_id.factor_inv != 0:
					cal_qty = self.product_qty/self.secondary_uom_id.factor_inv
					self.secondary_quantity = cal_qty
			if self.secondary_uom_id.uom_type =='smaller':
				cal_qty = self.product_uom_qty * self.secondary_uom_id.factor
				self.secondary_quantity = cal_qty


class StockInventory(models.Model):
	_inherit = 'stock.inventory'

	def action_validate(self):
		res=super(StockInventory, self).action_validate()
		inventory_lines=self._get_inventory_lines_values()
		quant_id = False
		if inventory_lines:
			quant_id = self.env['stock.quant'].search([('product_id','=',inventory_lines[0]['product_id']),('location_id','=',inventory_lines[0]['location_id'])], limit=1)
		if self.state == 'done':
			for line in self.line_ids:
				if quant_id:
					quant_id.write({'secondary_quantity':line.secondary_quantity, 'secondary_uom_id':line.secondary_uom_id.id})
		return res