# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeTitle(models.Model):
    _name = 'hr.employee.title'
    _description = 'HR Employee Title Name'

    name = fields.Char(
        string='Title Name',
        required=True
    )
