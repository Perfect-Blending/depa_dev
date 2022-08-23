from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class depa_welfare_type_lines(models.Model):
    _name = 'depa_welfare_type_lines'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    depa_welfare_type_lines_id = fields.Many2one(
        'depa_welfare_types'
    )