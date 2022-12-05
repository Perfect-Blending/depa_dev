# -*- coding: utf-8 -*-
from openerp import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fin_can_approve = fields.Boolean(string='FIN approver',)
