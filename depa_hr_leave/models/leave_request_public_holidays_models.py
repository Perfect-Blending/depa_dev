# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError

class public_holidays(models.Model):
    _name = 'leave_request_public_holidays'

    fiscal_year_id = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        required=True,
        string="ปีงบประมาณ"
    )

    fiscal_year = fields.Char(
        string="ปีงบประมาณ"
    )

    leave_request_public_holidays_lines_ids = fields.One2many(
        "leave_request_public_holidays_lines",
        "leave_request_public_holidays_lines_id",
        copy=True
    )

    active = fields.Boolean(
        default=True,
    )

    @api.onchange('fiscal_year_id')
    def _fiscal_year_id_change(self):
        for line in self:
            if line.fiscal_year_id:
                line.fiscal_year = line.fiscal_year_id.fiscal_year

    def name_get(self):
        return [(rec.id, rec.fiscal_year_id.fiscal_year) for rec in self]

class leave_request_public_holidays_lines(models.Model):
    _name = 'leave_request_public_holidays_lines'

    name = fields.Char(
        string="ชื่อ"
    )

    date = fields.Date(
        required=True
    )

    leave_request_public_holidays_lines_id = fields.Many2one(
        "leave_request_public_holidays"
    )
