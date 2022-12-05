# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ConsumePartsSetting(models.TransientModel):

	_inherit = 'res.config.settings'

	consume_parts = fields.Boolean(string="Consume Parts from Stock",default=False)

	location_id = fields.Many2one('stock.location',string="Inventory Location")

	location_dest_id = fields.Many2one('stock.location',string="Consumed Part Location")

	def set_values(self):
		super(ConsumePartsSetting, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('bi_car_repair_management.consume_parts', self.consume_parts)
		self.env['ir.config_parameter'].sudo().set_param('bi_car_repair_management.location_id', self.location_id.id)
		self.env['ir.config_parameter'].sudo().set_param('bi_car_repair_management.location_dest_id', self.location_dest_id.id)

	@api.model
	def get_values(self):
		res = super(ConsumePartsSetting, self).get_values()
		res.update({
			'consume_parts':bool(self.env['ir.config_parameter'].sudo().get_param('bi_car_repair_management.consume_parts')),
			'location_id': int(self.env['ir.config_parameter'].sudo().get_param('bi_car_repair_management.location_id')),
			'location_dest_id' : int(self.env['ir.config_parameter'].sudo().get_param('bi_car_repair_management.location_dest_id'))
			})
		return res