# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
TRANS_TYPE = [
    ('add', '+'),
    ('minus', '-')
]
class point_history_lines(models.Model):
    _name = 'point_history_lines'
    _order = "on_date desc"

    desc = fields.Text(
        string="List name",
        required=True,
        readonly=True
    )

    on_date = fields.Datetime(
        string="On date",
        required=True,
        readonly=True
    )

    point_type = fields.Selection(
        TRANS_TYPE,
        string="Type",
        required=True,
        readonly=True
    )

    point_usage = fields.Float(
        string="Point Usage",
        required=True,
        readonly=True
    )

    point_balance = fields.Float(
        string="Point Balance",
        required=True,
        readonly=True
    )

    depa_welfare_id = fields.Many2one(
        "depa_welfare",
        string="Ref.",
        readonly=True
    )

    wel_doc_no = fields.Char(
        string="เลขที่เอกสาร",
        readonly=True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        readonly=True
    )

    welfare_fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        string="Year",
        readonly=True
    )

    point_history_lines_id = fields.Many2one(
        "user_profile",
        readonly=True
    )