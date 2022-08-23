# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models
from odoo import tools, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class depa_group(models.Model):
    _name = 'depa_group'

    name = fields.Char(
        string="ชื่อกลุ่มงาน",
        required=True
    )

    department_group_ids = fields.One2many(
        'hr.department',
        'department_group_id',
        string="ฝ่าย/ส่วน ใต้สังกัด"
    )

    employee_group_ids = fields.One2many(
        'hr.employee',
        'employee_group_id',
        string="พนักงาน"
    )

class hr_department_group_inherit(models.Model):
    _inherit = 'hr.department'

    department_group_id = fields.Many2one(
        'depa_group',
        string="กลุ่มงาน"
    )