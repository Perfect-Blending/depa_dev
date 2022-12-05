# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fin_can_approve = fields.Boolean(string='FIN approver',)
    is_dummy = fields.Boolean(String='Dummy')


class HrDepartment(models.Model):
    _inherit = 'hr.department'