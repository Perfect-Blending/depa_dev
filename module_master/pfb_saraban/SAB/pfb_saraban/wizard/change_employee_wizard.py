# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ChangeEmployeeWizard(models.TransientModel):
    _name = "change.employee.wizard"

    employee_id = fields.Many2one(
        'hr.employee',
        string="Approve User"
    )

    @api.multi
    def action_approve(self):

        return True