# -*- coding: utf-8 -*-f
from dateutil.relativedelta import relativedelta
import base64

from odoo import api, fields, models
from odoo import tools, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class user_relative(models.Model):
    _name = 'user_relative'

    name = fields.Char(string="Name", required=True)
    relationship = fields.Selection([
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('children', 'Children')
    ],
        required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        required=True
    )
    birthday = fields.Date(string="Birthday", required=True)

    @api.model
    def create(self, vals):
        res = super(user_relative, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(user_relative, self).write(vals)
        return res
