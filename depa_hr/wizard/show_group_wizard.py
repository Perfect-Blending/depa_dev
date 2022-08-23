from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class show_group_wizard(models.TransientModel):
    _name = 'show_group_wizard'

    def get_my_result(self):
        user_id = self.env.uid
        employee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_id)
        ], limit=1)
        return employee.employee_group_ids.ids

    group_ids = fields.Many2many(
        "hr_employee_group",
        "hr_employee_show_group_rel",
        "show_group_id",
        "hr_employee_group_id",
        string='ผลการประเมิน',
        default=get_my_result
    )