# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class kpi_master_models(models.Model):
    _name = 'budget_master'
    _order = 'fiscal_year desc'

    fiscal_year = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        string="ปีงบประมาณ",
        required=True,
        copy=True
    )
    note = fields.Text(
        string="หมายเหตุ",
        copy=True
    )
    budget_master_lines_ids = fields.One2many(
        "budget_master_lines",
        "budget_master_lines_id",
        string="รายการงบประมาณ",
        copy=True
    )

class budget_master_lines_models(models.Model):
    _name = 'budget_master_lines'

    budget_master_lines_id = fields.Many2one(
        "budget_master",
        required = True,
        ondelete = "cascade"
    )
    budget_master_fiscal_year = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        string="ปีงบประมาณ",
        compute='_depends_fiscal_year',
        store=True,
    )
    projects_and_plan = fields.Many2one(
        "account.analytic.account",
        string="ชื่องบประมาณ"
    )
    code = fields.Char(
        string="รหัสงบประมาณ"
    )
    name = fields.Char(
        string="ชื่อโครงการ"
    )
    project_type = fields.Selection(
        [
            ('new', 'โครงการใหม่'),
            ('old', 'โครงการต่อเนื่อง')
        ],
        string="ประเภทโครงการ"
    )
    budget = fields.Float(
        string="งบประมาณ"
    )
    host_department_id = fields.Many2one(
        "hr.department",
        string="งบประมาณของฝ่าย"
    )
    budget_manager = fields.Many2one(
        "hr.employee",
        string="ผู้รับผิดชอบงบประมาณ"
    )

    @api.onchange('projects_and_plan')
    def _projects_and_plan_change(self):
        for rec in self:
            rec.code = rec.projects_and_plan.code
            rec.name = rec.projects_and_plan.group_id.name
            rec.budget = rec.projects_and_plan.budget
            rec.budget_manager = rec.projects_and_plan.manager
            rec.project_type = rec.projects_and_plan.project_type

    @api.multi
    @api.depends('budget_master_lines_id.fiscal_year')
    def _depends_fiscal_year(self):
        for rec in self:
            rec.budget_master_fiscal_year = rec.budget_master_lines_id.fiscal_year.id