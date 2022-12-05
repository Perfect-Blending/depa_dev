# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################


from odoo import api, models, _, fields
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'


	@api.multi
	def _prepare_stock_moves(self, picking):
		""" Prepare the stock moves data for one order line. This function returns a list of
		dictionary ready to be used in stock.move's create()
		"""
		res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking=picking)
		config_id = self.env['res.config.settings'].sudo().search([],limit=1,order='id desc')
		if config_id.allow_bundle == True:
			self.ensure_one()
			res = []
			if self.product_id.type not in ['product', 'consu']:
				return res
			qty = 0.0
			price_unit = self._get_stock_move_price_unit()
			for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
				qty += move.product_qty
			if  self.product_id.pack_ids:
				for item in self.product_id.pack_ids:
					template = {
						'name': item.product_id.name or '',
						'product_id': item.product_id.id,
						'product_uom': item.uom_id.id,
						'date': self.order_id.date_order,
						'date_expected': self.date_planned,
						'location_id': self.order_id.partner_id.property_stock_supplier.id,
						'location_dest_id': self.order_id._get_destination_location(),
						'picking_id': picking.id,
						'partner_id': self.order_id.dest_address_id.id,
						'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
						'state': 'draft',
						'purchase_line_id': self.id,
						'company_id': self.order_id.company_id.id,
						'price_unit': price_unit,
						'picking_type_id': self.order_id.picking_type_id.id,
						'group_id': self.order_id.group_id.id,
						'origin': self.order_id.name,
						'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
						'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
						'pack_id' : item.id,
					}
					diff_quantity = item.qty_uom
					if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
						template['product_uom_qty'] = diff_quantity * self.product_qty
						res.append(template)
				return res
			else:
				template = {
				'name': self.name or '',
				'product_id': self.product_id.id,
				'product_uom': self.product_uom.id,
				'date': self.order_id.date_order,
				'date_expected': self.date_planned,
				'location_id': self.order_id.partner_id.property_stock_supplier.id,
				'location_dest_id': self.order_id._get_destination_location(),
				'picking_id': picking.id,
				'partner_id': self.order_id.dest_address_id.id,
				'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
				'state': 'draft',
				'purchase_line_id': self.id,
				'company_id': self.order_id.company_id.id,
				'price_unit': price_unit,
				'picking_type_id': self.order_id.picking_type_id.id,
				'group_id': self.order_id.group_id.id,
				'origin': self.order_id.name,
				'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
				'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
			}
				diff_quantity = self.product_qty - qty
				if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
					template['product_uom_qty'] = diff_quantity
					res.append(template)
			return res
		else:
			return res 

	@api.multi
	def _update_received_qty(self):
		
		config_id = self.env['res.config.settings'].sudo().search([],limit=1,order='id desc')
		for line in self:
			def check_product(x):
				for rec in line.product_id.pack_ids:
					if x == rec.product_id:
						return x
			received = 0
			received += line.qty_received
			qty = 0.0
			total = 0.0
			flag = False
			count = 0
			done_list = [] 
			deliver_list = []
			move_list = []
			products = []
			filtered = []
			vals_list = []
			picking_ids = self.env['stock.picking'].search([('origin','=',line.order_id.name)])
			for pick in picking_ids:
				for move_is in pick.move_ids_without_package:
					if move_is.product_id not in products:
						products.append(move_is.product_id)
	
			pro = filter(check_product,products)
			for product in pro:
				filtered.append(product)
			for pick in picking_ids:
				for move_is in pick.move_ids_without_package:
					if move_is.product_id in filtered:
						if move_is.pack_id in line.product_id.pack_ids:
							move_list.append(move_is.product_uom_qty)
							done_list.append(move_is.quantity_done)
							
		
			stock_move = self.env['stock.move'].search([('origin','=',line.order_id.name)])
			vals = []
			if line.product_id.is_pack == True and config_id.allow_bundle == True:
				list_of_sub_product = []
				for product_item in line.product_id.pack_ids:
					list_of_sub_product.append(product_item.product_id)
				for move in stock_move:
					if count == 0:
						if move.state == 'done' and move.product_uom_qty == move.quantity_done:
							flag = True
							for picking in picking_ids:
								for move_is in picking.move_ids_without_package:
									if sum(move_list) == 0:
										pass
									else:
										deliver_qty =(line.product_qty*sum(done_list))/sum(move_list)
										line.qty_received = int(deliver_qty)
										deliver_list.append(line.qty_received)           
					elif move.state == 'confirmed':
						flag = 'confirmed'
						count = count+1
						done_list.append(move.quantity_done)
						for picking in picking_ids:
							for move_is in picking.move_ids_without_package:

								if sum(move_list) == 0:
									pass
								else:
									deliver_qty =(line.product_qty*sum(done_list))/sum(move_list)
									line.qty_received = int(deliver_qty)
									deliver_list.append(line.qty_received)					
			else:                            
				# In case of a BOM in kit, the products delivered do not correspond to the products in
				# the PO. Therefore, we can skip them since they will be handled later on.
				for move in line.move_ids.filtered(lambda m: m.product_id == line.product_id):
					if move.state == 'done':
						if move.location_dest_id.usage == "supplier":
							if move.to_refund:
								total -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
						elif move.origin_returned_move_id._is_dropshipped() and not move._is_dropshipped_returned():
							# Edge case: the dropship is returned to the stock, no to the supplier.
							# In this case, the received quantity on the PO is set although we didn't
							# receive the product physically in our stock. To avoid counting the
							# quantity twice, we do nothing.
							pass
						else:
							total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
							
				line.qty_received = total  

				    
            

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'     

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	allow_bundle = fields.Boolean('Allow bundle in purchase')

	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		allow_bundle = self.env['ir.config_parameter'].sudo().get_param('product_bundle_pack.allow_bundle')
		res.update(
			allow_bundle = allow_bundle,
		)
		return res

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('product_bundle_pack.allow_bundle', self.allow_bundle)

class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'

class StockMoveInherit(models.Model):
	_inherit = 'stock.move'

	pack_id = fields.Many2one('product.pack',string="PACK")
	

class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'

	pack_id = fields.Many2one('product.pack',string="PACK")
	