# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")
	secondary_uom_name = fields.Char(string='Unit of Measure Name', related='secondary_uom_id.name', readonly=True)
	secondary_qty = fields.Float(
		'Secondary Qty', compute='_compute_second_quantities', search='_search_second_qty_available',
		digits=dp.get_precision('Product Unit of Measure'))
	is_secondary_uom = fields.Boolean("Secondary Unit")

	@api.depends(
		'product_variant_ids',
		'product_variant_ids.stock_move_ids.secondary_quantity',
		'product_variant_ids.stock_move_ids.state',
	)
	def _compute_second_quantities(self):
		res = self._compute_second_quantities_dict()
		for template in self:
			template.secondary_qty = res[template.id]['second_qty_available']

	def _compute_second_quantities_dict(self):
		# TDE FIXME: why not using directly the function fields ?
		variants_available = self.mapped('product_variant_ids')._product_available()
		prod_available = {}
		for template in self:
			secondary_qty = 0
			for p in template.product_variant_ids:
				secondary_qty += variants_available[p.id]["second_qty_available"]
			prod_available[template.id] = {
				"second_qty_available": secondary_qty,
			}
		return prod_available

	def _search_second_qty_available(self, operator, value):
		domain = [('qty_available', operator, value)]
		product_variant_ids = self.env['product.product'].search(domain)
		return [('product_variant_ids', 'in', product_variant_ids.ids)]

	def action_open_secondary_quants(self):
		self.env['stock.quant']._merge_quants()
		self.env['stock.quant']._unlink_zero_quants()
		products = self.mapped('product_variant_ids')
		action = self.env.ref('stock.product_open_quants').read()[0]
		action['domain'] = [('product_id', 'in', products.ids)]
		action['context'] = {'search_default_internal_loc': 1}
		return action

class ProductProduct(models.Model):
	_inherit = 'product.product'

	secondary_qty = fields.Float(
		'Secondary Qty', compute='_compute_second_quantities', search='_search_second_qty_available',
		digits=dp.get_precision('Product Unit of Measure'))

	@api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
	def _compute_second_quantities(self):
		res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
		for product in self:
			product.secondary_qty = res[product.id]['second_qty_available']

	def _search_second_qty_available(self, operator, value):
		if value == 0.0 and operator == '>' and not ({'from_date', 'to_date'} & set(self.env.context.keys())):
			product_ids = self._search_qty_available_new(
				operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
				self.env.context.get('package_id')
			)
			return [('id', 'in', product_ids)]
		return self._search_product_quantity(operator, value, 'secondary_qty')

	def _search_product_quantity(self, operator, value, field):
		# TDE FIXME: should probably clean the search methods
		# to prevent sql injections
		if field not in ('secondary_qty','qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'):
			raise UserError(_('Invalid domain left operand %s') % field)
		if operator not in ('<', '>', '=', '!=', '<=', '>='):
			raise UserError(_('Invalid domain operator %s') % operator)
		if not isinstance(value, (float, int)):
			raise UserError(_('Invalid domain right operand %s') % value)

		# TODO: Still optimization possible when searching virtual quantities
		ids = []
		# Order the search on `id` to prevent the default order on the product name which slows
		# down the search because of the join on the translation table to get the translated names.
		for product in self.with_context(prefetch_fields=False).search([], order='id'):
			if OPERATORS[operator](product[field], value):
				ids.append(product.id)
		return [('id', 'in', ids)]

	def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
		domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
		domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
		dates_in_the_past = False
		# only to_date as to_date will correspond to qty_available
		to_date = fields.Datetime.to_datetime(to_date)
		if to_date and to_date < fields.Datetime.now():
			dates_in_the_past = True

		domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
		domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
		if lot_id is not None:
			domain_quant += [('lot_id', '=', lot_id)]
		if owner_id is not None:
			domain_quant += [('owner_id', '=', owner_id)]
			domain_move_in += [('restrict_partner_id', '=', owner_id)]
			domain_move_out += [('restrict_partner_id', '=', owner_id)]
		if package_id is not None:
			domain_quant += [('package_id', '=', package_id)]
		if dates_in_the_past:
			domain_move_in_done = list(domain_move_in)
			domain_move_out_done = list(domain_move_out)
		if from_date:
			domain_move_in += [('date', '>=', from_date)]
			domain_move_out += [('date', '>=', from_date)]
		if to_date:
			domain_move_in += [('date', '<=', to_date)]
			domain_move_out += [('date', '<=', to_date)]

		Move = self.env['stock.move']
		Quant = self.env['stock.quant']
		domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
		domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
		moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
		moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
		quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
		second_quants_res = dict((item['product_id'][0], item['secondary_quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'secondary_quantity'], ['product_id'], orderby='id'))
		if dates_in_the_past:
			# Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
			domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
			domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
			moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
			moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

		res = dict()
		for product in self.with_context(prefetch_fields=False):
			product_id = product.id
			rounding = product.uom_id.rounding
			res[product_id] = {}
			if dates_in_the_past:
				qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
				second_qty_available = second_quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
			else:
				qty_available = quants_res.get(product_id, 0.0)
				second_qty_available = second_quants_res.get(product_id, 0.0)
			res[product_id]['second_qty_available'] = float_round(second_qty_available, precision_rounding=rounding)
			res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
			res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
			res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
			res[product_id]['virtual_available'] = float_round(
				qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
				precision_rounding=rounding)

		return res

	# Be aware that the exact same function exists in product.template
	def action_open_secondary_quants(self):
		self.env['stock.quant']._merge_quants()
		self.env['stock.quant']._unlink_zero_quants()
		action = self.env.ref('stock.product_open_quants').read()[0]
		action['domain'] = [('product_id', '=', self.id)]
		action['context'] = {'search_default_internal_loc': 1}
		return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4::
