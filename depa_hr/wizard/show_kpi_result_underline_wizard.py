from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class show_kpi_result_underline_wizard(models.TransientModel):
    _name = 'show_kpi_result_underline_wizard'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    def get_my_underline_employee(self, employee):
        employee_ids = []
        if employee.child_ids:
            employee_ids.extend(employee.child_ids.ids)
            for step1 in employee.child_ids:
                if step1.child_ids:
                    employee_ids.extend(step1.child_ids.ids)
                    for step2 in step1.child_ids:
                        if step2.child_ids:
                            employee_ids.extend(step2.child_ids.ids)
                            for step3 in step2.child_ids:
                                if step3.child_ids:
                                    employee_ids.extend(step3.child_ids.ids)
                                    for step4 in step3.child_ids:
                                        if step4.child_ids:
                                            employee_ids.extend(step4.child_ids.ids)
                                            for step5 in step4.child_ids:
                                                if step5.child_ids:
                                                    employee_ids.extend(step5.child_ids.ids)

        return employee_ids

    def get_my_underline_result(self, employee, fiscal_year, round):
        employee_ids = self.get_my_underline_employee(employee)
        result_ids = self.env['hr_employee_kpi_result'].search([
            ('employee_kpi_result_id', 'in', employee_ids),
            ('kpi_round_setting_id', '=', fiscal_year)
        ]).ids
        if round:
            result_ids = self.env['hr_employee_kpi_result'].search([
                ('employee_kpi_result_id', 'in', employee_ids),
                ('kpi_round_setting_id', '=', fiscal_year),
                ('kpi_round_setting_lines_id', '=', round)
            ]).ids
        return result_ids

    def get_result(self):
        user_id = self.env.uid
        employee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_id)
        ], limit=1)
        result_ids = self.get_my_underline_result(employee, self._default_fiscal_year(), False)
        # print(employee)
        # print(result_ids)
        return result_ids

    kpi_result_underline_ids = fields.Many2many(
        "hr_employee_kpi_result",
        "hr_employee_show_kpi_result_underline_rel",
        "show_kpi_result_underline_id",
        "hr_employee_kpi_result_id",
        string='ผลการประเมิน',
        default=get_result,
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
    @api.onchange('kpi_round_setting_id')
    def _onchange_kpi_round_setting_id(self):
        self.kpi_round_setting_lines_id = False
        user_id = self.env.uid
        employee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_id)
        ], limit=1)
        result_ids = self.get_my_underline_result(employee, self.kpi_round_setting_id.id, False)
        self.kpi_result_underline_ids = [(6, 0, result_ids)]

    @api.onchange('kpi_round_setting_lines_id')
    def _onchange_kpi_round_setting_lines_id(self):
        user_id = self.env.uid
        employee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_id)
        ], limit=1)
        result_ids = self.get_my_underline_result(employee, self.kpi_round_setting_id.id, self.kpi_round_setting_lines_id.id)
        self.kpi_result_underline_ids = [(6, 0, result_ids)]