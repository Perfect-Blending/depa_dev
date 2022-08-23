# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_title_name = fields.Selection(
        [
            ('นาย', 'นาย'),
            ('นาง', 'นาง'),
            ('นางสาว', 'นางสาว')
        ],
        string='คำนำหน้า',
    )
    emp_code = fields.Char(
        string='รหัสพนักงาน',
        required=True,
    )
    start_date = fields.Date(
        string='วันที่เริ่มงาน'
    )
    end_date = fields.Date(
        string='วันที่พ้นสภาพ'
    )
    pass_probation_date = fields.Date(
        string='วันที่บรรจุ'
    )
    relative_ids = fields.One2many(
        string='Relatives',
        comodel_name='hr.employee.relative',
        inverse_name='employee_id',
    )
