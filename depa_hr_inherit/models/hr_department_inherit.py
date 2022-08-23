
from odoo import fields, models


class Department(models.Model):
    _inherit = 'hr.department'

    department_code = fields.Char(
        string="Code"
    )
    name_en = fields.Char(
        string="ชื่อแผนก(EN)"
    )

