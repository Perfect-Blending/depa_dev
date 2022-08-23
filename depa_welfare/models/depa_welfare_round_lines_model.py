from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class depa_welfare_round_lines(models.Model):
    _name = 'depa_welfare_round_lines'

    welfare_round = fields.Integer(
        default=1,
        required=True
    )
    welfare_start = fields.Date(
        required=True
    )
    welfare_end = fields.Date(
        required=True
    )
    depa_welfare_round_lines_id = fields.Many2one(
        "depa_welfare_rounds"
    )

    def name_get(self):
        return [(name.id, str(name.welfare_round) + '|' + str(name.welfare_start) + ' - ' + str(name.welfare_end)) for name in self]
