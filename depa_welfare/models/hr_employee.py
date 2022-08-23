# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError

class hr_employee_inherit(models.Model):
    _inherit = 'hr.employee'

    def _default_employee_id(self):
        employee_obj = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ])
        return employee_obj

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    current_point = fields.Float(
        compute='_compute_my_point',
        store=True
    )
    emp_id = fields.Char(
        default=lambda self: self._default_employee_id().id
    )
    # emp_code = fields.Char(string="Employee Code")
    emp_point = fields.Integer(string="Employee Point")
    # father_name = fields.Char(string="ชื่อบิดา")
    # father_birthday = fields.Date(string="วันเกิดบิดา")
    # mother_name = fields.Char(string="ชื่อมารดา")
    # mother_birthday = fields.Date(string="วันเกิดมารดา")

    point_history_lines = fields.One2many(
        "point_history_lines",
        "employee_id",
        "Point Usage History",
        readonly=True
    )
    
    relative_lines_ids = fields.One2many(
        "user_relative",
        "employee_id",
        "User Relative",
        copy=True
    )
    is_in_probation = fields.Boolean()

    @api.depends('emp_code')
    def _compute_my_point(self):
        employee_point = self.env['depa_welfare_hr_lines'].search([
            ('employee_id', '=', self._default_employee_id().id),
            ('hr_employee_id.year', '=', self._default_fiscal_year())
        ], limit=1)

        if employee_point:
            return employee_point.point




