# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class kpi_master_models(models.Model):
    _name = 'kpi_master'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    fiscal_year = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        string="ปีงบประมาณ",
        required=True,
        copy=True,
        default=_default_fiscal_year
    )
    is_used = fields.Boolean(
        default=False
    )

    kpi_master_lines_ids = fields.One2many(
        "kpi_master_lines",
        "kpi_master_lines_id",
        string="KPI",
        copy=True
    )


class kpi_master_lines_models(models.Model):
    _name = 'kpi_master_lines'

    def _get_fiscal_year(self):
        return self.kpi_master_lines_id.fiscal_year.id

    def _get_default_definition_lines(self):
        list = []
        for i in range(5):
            list.append((
                    0,
                    0,
                    {
                        'kpi_definition_lines_id': self.id,
                        'kpi_definition_level': str(i+1)
                    }
                ))

        return list

    kpi_master_lines_id = fields.Many2one(
        "kpi_master"
    )
    kpi_master_fiscal_year = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        string="ปีงบประมาณ",
        compute="_depends_fiscal_year",
        store=True,
        default=_get_fiscal_year
    )

    kpi_master_code = fields.Char(
        string="รหัส KPI"
    )

    kpi_master_name = fields.Text(
        string="ชื่อ KPI"
    )
    kpi_master_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 8)
    )
    # kpi_master_target = fields.Float(
    #     string="เป้าหมาย",
    #     digits=(10, 2)
    # )
    kpi_master_def = fields.Text(
        string="คำจำกัดความ"
    )
    # kpi_master_unit = fields.Many2one(
    #     'uom.uom',
    #     'หน่วย'
    # )
    source_id = fields.Many2one(
        "source_master",
        string="ที่มา",
        required=True,
        default=False
    )
    kpi_master_type = fields.Selection(
        [
            ('corporate', 'Corporate'),
            ('common', 'Common'),
            ('function', 'Function'),
            ('contribution', 'Contribution'),
        ],
        string="ประเภท KPI",
        default='corporate'
    )
    kpi_master_bsc = fields.Selection(
        [
            ('F', 'Financial'),
            ('C', 'Customer'),
            ('I', 'Internal'),
            ('O', 'Learning'),
        ],
        string="BSC"
    )
    kpi_budget_code_id = fields.Many2many(
        'budget_master_lines',
        string="รหัสงบประมาณ",
        required=True,
        domain="[('budget_master_fiscal_year', '=', kpi_master_fiscal_year)]"
    )
    kpi_budget_amount = fields.Float(
        string="งบประมาณรวม",
        digits=(10, 2),
        compute='_compute_kpi_budget_amount',
        store=True,
    )

    kpi_definition_lines_ids = fields.One2many(
        'kpi_definition_lines',
        'kpi_definition_lines_id',
        required=True,
        copy=True,
        default=_get_default_definition_lines
    )
    kpi_target_lines_ids = fields.One2many(
        'kpi_target_lines',
        'kpi_target_lines_id',
        required=True,
        copy=True,
    )


    @api.multi
    @api.depends('kpi_budget_code_id')
    def _compute_kpi_budget_amount(self):
        for rec in self:
            sum = 0
            for budget in rec.kpi_budget_code_id:
                sum += budget.budget
            rec.kpi_budget_amount = sum

    @api.multi
    @api.depends('kpi_master_lines_id.fiscal_year')
    def _depends_fiscal_year(self):
        for rec in self:
            rec.kpi_master_fiscal_year = rec.kpi_master_lines_id.fiscal_year.id

    @api.multi
    def name_get(self):
        res = []
        for obj in self:
            name = obj.kpi_master_name
            res.append((obj.id, name))
        return res

class kpi_target_lines(models.Model):
    _name = 'kpi_target_lines'

    kpi_target_lines_id = fields.Many2one(
        "kpi_master_lines",
        required=True
    )
    kpi_target_target = fields.Float(
        string="เป้าหมาย",
        digits=(10, 2),
    )
    kpi_target_unit = fields.Many2one(
        'uom.uom',
        'หน่วย'
    )

class kpi_definition_lines(models.Model):
    _name = 'kpi_definition_lines'

    kpi_definition_lines_id = fields.Many2one(
        "kpi_master_lines",
        required=True
    )

    kpi_definition_level = fields.Selection(
        [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5')
        ],
        string="ระดับคะแนน"
    )
    kpi_definition_name = fields.Text(
        string="คำจำกัดความ"
    )
    # kpi_definition_target = fields.Float(
    #     string="เป้าหมาย",
    #     digits=(10, 2)
    # )
    # kpi_definition_target_target_start = fields.Float(
    #     string="เป้าหมายเริ่มต้น"
    # )
    # kpi_definition_target_target_end = fields.Float(
    #     string="เป้าหมายสิ้นสุด"
    # )
    kpi_definition_unit = fields.Many2one(
        'uom.uom',
        'หน่วย'
    )

    kpi_definition_target_line_ids = fields.One2many(
        "kpi_definition_target_lines",
        "kpi_definition_target_lines_id",
        string="KPI Definition Target",
        copy=True,
        readonly=False
    )

class kpi_definition_target_lines(models.Model):
    _name = 'kpi_definition_target_lines'

    kpi_definition_target_lines_id = fields.Many2one(
        "kpi_definition_lines",
        required=True
    )

    kpi_definition_target_target_end = fields.Float(
        string="เป้าหมายสิ้นสุด",
        digits=(10, 2)
    )
    kpi_definition_target_target_start = fields.Float(
        string="เป้าหมายเริ่มต้น",
        digits=(10, 2)
    )

    kpi_definition_target_unit = fields.Many2one(
        'uom.uom',
        'หน่วย'
    )

