from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class depa_welfare_rounds(models.Model):
    _name = 'depa_welfare_rounds'

    fiscal_year_id = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        required=True
    )
    welfare_year = fields.Char(
        compute='_fiscal_year_id_change',
    )
    welfare_year_start = fields.Date(
        required=True
    )
    welfare_year_end = fields.Date(
        required=True
    )
    depa_welfare_round_lines_ids = fields.One2many(
        "depa_welfare_round_lines",
        "depa_welfare_round_lines_id",
        copy=True
    )
    active = fields.Boolean(
        default=True
    )

    @api.depends('fiscal_year_id')
    def _fiscal_year_id_change(self):
        for line in self:
            if line.fiscal_year_id:
                line.welfare_year = line.fiscal_year_id.fiscal_year
                line.welfare_year_start = line.fiscal_year_id.date_start
                line.welfare_year_end = line.fiscal_year_id.date_end