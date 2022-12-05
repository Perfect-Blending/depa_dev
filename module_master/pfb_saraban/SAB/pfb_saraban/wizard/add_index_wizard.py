# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class AddIndexWizard(models.TransientModel):
    _name = "add.index.wizard"

    approve_type = fields.Selection(selection=[
        ('require', 'Is require to approve'),
        ('comments', 'Comments only')
    ],string="Approve type")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Approve User"
    )

    @api.multi
    def action_approve(self):

        return True