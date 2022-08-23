from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class kpi_round_setting(models.Model):
    _name = 'kpi_round_setting'

    fiscal_year_id = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        required=True
    )
    kpi_year = fields.Char(
        # compute='_fiscal_year_id_change',
        # store=False
    )
    kpi_year_start = fields.Date(
        required=True
    )
    kpi_year_end = fields.Date(
        required=True
    )
    kpi_round_setting_lines_ids = fields.One2many(
        "kpi_round_setting_lines",
        "kpi_round_setting_lines_id",
        copy=True
    )
    active = fields.Boolean(
        default=True
    )
    show_sent_button = fields.Boolean(
        default=False
    )

    @api.onchange('fiscal_year_id')
    def _fiscal_year_id_change(self):
        # print(self)
        for line in self:
            if line.fiscal_year_id:
                line.kpi_year = line.fiscal_year_id.fiscal_year
                line.kpi_year_start = line.fiscal_year_id.date_start
                line.kpi_year_end = line.fiscal_year_id.date_end

    def name_get(self):
        return [(rec.id, rec.fiscal_year_id.fiscal_year) for rec in self]

class kpi_round_setting_lines(models.Model):
    _name = 'kpi_round_setting_lines'

    kpi_round = fields.Integer(
        default=1,
        required=True
    )
    kpi_start = fields.Date(
        required=True
    )
    kpi_end = fields.Date(
        required=True
    )
    kpi_round_setting_lines_id = fields.Many2one(
        "kpi_round_setting"
    )

    def name_get(self):
        return [(rec.id, str(rec.kpi_round)) for rec in self]