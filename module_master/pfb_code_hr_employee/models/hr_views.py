from odoo import models, fields, api, _


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    hr_code_id = fields.Char(string="Personnel Code ")



