# -*- coding: utf-8 -*-
# Copyright 2019 Linksoft Mitra Informatika
import logging

from odoo import models, fields
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

PARAMS = {
    'm2x_create': 'web_m2x_options.create',
    'm2x_create_edit': 'web_m2x_options.create_edit',
    'm2x_m2o_dialog': 'web_m2x_options.m2o_dialog',
    'm2x_search_more': 'web_m2x_options.search_more'
}


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    m2x_create = fields.Boolean(string="Show Create", default=True)
    m2x_create_edit = fields.Boolean(string="Show Create & Edit", default=True)
    m2x_m2o_dialog = fields.Boolean(string="Show M2O Dialog", default=True)
    m2x_search_more = fields.Boolean(string="Show Search More", default=True)
    m2x_limit = fields.Integer(string="Limit", default=7, config_parameter="web_m2x_options.limit")

    def get_values(self):
        ir_config_parameter_obj = self.env['ir.config_parameter'].sudo()

        res = super(ResConfigSettings, self).get_values()
        for field_name, key_name in PARAMS.items():
            if not ir_config_parameter_obj.get_param(key_name):
                default_value = self._fields.get(field_name).default(self._name)
                ir_config_parameter_obj.create({'key': key_name, 'value': str(False or default_value)})
            res[field_name] = safe_eval(ir_config_parameter_obj.get_param(key_name))
        return res

    def set_values(self):
        ir_config_parameter_obj = self.env['ir.config_parameter'].sudo()

        super(ResConfigSettings, self).set_values()
        for field_name, key_name in PARAMS.items():
            value = ir_config_parameter_obj.get_param(key_name)
            if not value:
                ir_config_parameter_obj.create({'key': key_name, 'value': self[field_name]})
            else:
                icp = ir_config_parameter_obj.search([('key', '=', key_name)])
                icp.write({'key': key_name, 'value': str(self[field_name])})
