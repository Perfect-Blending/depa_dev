from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class depa_welfare_approval_lines(models.Model):
    _name = 'depa_welfare_state_setting'

    code = fields.Char(
        required=True
    )

    name = fields.Char(
        required=True
    )

    active = fields.Boolean(
        default=True
    )
