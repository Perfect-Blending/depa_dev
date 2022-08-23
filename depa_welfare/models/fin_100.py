# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


class fw_pfb_FS100_iinherit(models.Model):
    _inherit = 'fw_pfb_fin_system_100'

    is_welfare = fields.Boolean(
        string='Welfare',
        default=False,
    )
    fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        compute='_current_fiscal_year',
        store=True
    )
    welfare_round = fields.Integer(
        compute='_depends_welfare_round',
        store=True
    )
    welfare_round_start = fields.Date(
        readonly=True,
    )
    welfare_round_end = fields.Date(
        readonly=True,
    )

    @api.depends('is_welfare')
    def _current_fiscal_year(self):
        for rec in self:
            fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
                ('date_start', '<', date.today()),
                ('date_end', '>=', date.today()),
            ],limit=1)
            if fiscal_year_obj:
                rec.fiscal_year = fiscal_year_obj

    @api.depends('fiscal_year')
    def _depends_welfare_round(self):
        for rec in self:
            if rec.fiscal_year:
                welfare_round_line_obj = self.env['depa_welfare_round_lines'].search([
                    ('depa_welfare_round_lines_id.fiscal_year_id', '=', rec.fiscal_year.id),
                    ('welfare_start', '>=', date.today()),
                ], limit=1)
                if welfare_round_line_obj:
                    rec.welfare_round = welfare_round_line_obj.welfare_round
                    rec.welfare_round_start = welfare_round_line_obj.welfare_start
                    rec.welfare_round_end = welfare_round_line_obj.welfare_end


class fw_pfb_FS100Lines_inherit(models.Model):
    _inherit = 'fw_pfb_fin_system_100_line'

    is_fin_line_welfare_gbdi = fields.Boolean(
        default=False
    )