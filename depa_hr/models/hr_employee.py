# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError

class hr_employee_inherit(models.Model):
    _inherit = 'hr.employee'

    employee_types = fields.Selection(
        [
            ('operation', 'ระดับปฏิบัติการ'),
            ('academic', 'ระดับวิชาการ'),
            ('management', 'ระดับบริหาร')
        ],
        default='operation',
        required=True
    )
    is_kpi_dummy = fields.Boolean(
        string="Dummy ระบบ HR KPI",
        default=False
    )
    employee_kpi_result_ids = fields.One2many(
        "hr_employee_kpi_result",
        "employee_kpi_result_id"
    )
    employee_group_ids = fields.One2many(
        "hr_employee_group",
        "employee_group_id"
    )

class HrEmployeeKpiResult(models.Model):
    _name = 'hr_employee_kpi_result'
    _description = 'HR Employee KPI Result'
    _order = "employee_kpi_result_id asc, kpi_round_setting_id desc, kpi_round_setting_lines_id asc"

    employee_kpi_result_id = fields.Many2one(
        "hr.employee"
    )
    kpi_round_setting_id = fields.Many2one(
        'kpi_round_setting',
        required=True
    )
    kpi_round_setting_lines_id = fields.Many2one(
        'kpi_round_setting_lines',
        domain="[('kpi_round_setting_lines_id', '=', kpi_round_setting_id)]",
        required=True
    )
    kpi_main_id = fields.Many2one(
        'kpi_main'
    )
    kpi_grade = fields.Selection(
        [
            ('A', 'A'),
            ('B+', 'B+'),
            ('B', 'B'),
            ('C+', 'C+'),
            ('C', 'C'),
            ('D+', 'D+'),
            ('D', 'D'),
            ('F', 'F'),
        ],
        required=True
    )
    employee_id = fields.Integer()
    department_name = fields.Char(
        compute="_get_department_name_compute",
        store=True
    )

    @api.depends('employee_kpi_result_id', 'employee_id')
    def _get_department_name_compute(self):
        for rec in self:
            rec.department_name = rec.employee_kpi_result_id.department_id.name

    @api.onchange('kpi_round_setting_id')
    def onchange_kpi_round_setting_id(self):
        self.kpi_round_setting_lines_id = False
        self.kpi_main_id = False
        self.kpi_grade = False

    @api.onchange('kpi_round_setting_lines_id')
    def onchange_kpi_round_setting_lines_id(self):
        self.kpi_main_id = False
        self.kpi_grade = False
        kpi_main = self.env['kpi_main'].search([
            ('employee_id.id', '=', self.employee_id),
            ('kpi_fiscal_year', '=', self.kpi_round_setting_id.fiscal_year_id.id),
            ('kpi_round', '=', self.kpi_round_setting_lines_id.kpi_round),
            ('state', '=', 'done')
        ],limit=1)
        if kpi_main:
            self.kpi_main_id = kpi_main.id

    @api.model
    def create(self, vals):
        if vals['kpi_main_id']:
            kpi_main = self.env['kpi_main'].search([
                ('id', '=', vals['kpi_main_id'])
            ], limit=1)
            kpi_main.update({
                'kpi_grade': vals['kpi_grade']
            })
        res = super(HrEmployeeKpiResult, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'kpi_main_id' in vals:
            if vals['kpi_main_id']:
                kpi_main = self.env['kpi_main'].browse(int(vals['kpi_main_id']))
                if 'kpi_grade' in vals:
                    kpi_main.update({
                        'kpi_grade': vals['kpi_grade']
                    })
                else:
                    kpi_main.update({
                        'kpi_grade': self.kpi_grade
                    })

        else:
            if self.kpi_main_id:
                kpi_main = self.env['kpi_main'].browse(self.kpi_main_id.id)
                if 'kpi_grade' in vals:
                    kpi_main.update({
                        'kpi_grade': vals['kpi_grade']
                    })
                else:
                    kpi_main.update({
                        'kpi_grade': self.kpi_grade
                    })

        res = super(HrEmployeeKpiResult, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        if self.kpi_main_id:
            kpi_main = self.env['kpi_main'].browse(self.kpi_main_id.id)
            kpi_main.update({
                'kpi_grade': '-'
            })
        res = super(HrEmployeeKpiResult, self).unlink()
        return res

class hr_employee_group(models.Model):
    _name = 'hr_employee_group'
    _order = "employee_group_id asc"

    employee_group_id = fields.Many2one(
        "hr.employee"
    )
    kpi_round_setting_id = fields.Many2one(
        "kpi_round_setting",
        # required=True
    )
    kpi_round_setting_lines_id = fields.Many2one(
        'kpi_round_setting_lines',
        domain="[('kpi_round_setting_lines_id', '=', kpi_round_setting_id)]",
        # required=True
    )

    group_name = fields.Selection(
        [
            ('ก', 'ก'),
            ('ข', 'ข'),
            ('ค', 'ค'),
        ],
        required=True
    )
    remark = fields.Text(
        store=True
    )
    employee_id = fields.Integer()
    department_name = fields.Char(
        compute="_get_department_name_compute",
        store=True
    )
    group_date = fields.Date()

    @api.depends('employee_group_id', 'employee_id')
    def _get_department_name_compute(self):
        for rec in self:
            rec.department_name = rec.employee_group_id.department_id.name