# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class MakeApprovalWizardInherit(models.TransientModel):
    _inherit = "make.approval.wizard"

    memo = fields.Text('Memo', required=False)
    change_approver = fields.Many2many(
        'hr.employee',
        'change_approver_rel',
        'approval_id',
        'employee_id',
        string='Change Approver'
    )
    add_approver = fields.Many2many(
        'hr.employee',
        'add_approver_rel',
        'approval_id',
        'employee_id',
        string='Add Approver'
    )
    save_approver_button = fields.Boolean(
        default=False,
    )

    is_approver_change = fields.Boolean(
        default=False,
        compute='_onchange_approver',
    )

    @api.multi
    @api.onchange(
        'change_approver',
        'add_approver'
    )
    def _onchange_approver(self):
        for record in self:
            if record.change_approver or record.add_approver:
                record.is_approver_change = True


    @api.multi
    # @api.onchange('save_approver_button')
    def save_approver_button(self):
        sequence_count = 0
        setting_obj = self.env['document.internal.main'].search([
            ('id', '=', int(self.setting_id))
        ], limit=1, order='id')
        setting_line_obj = self.env['document.internal.main.setting.line'].search([
            ('setting_id', '=', int(self.setting_id))
        ], order='sequence')
        for setting_line in setting_line_obj:
            if setting_line.id == int(self.setting_line):
                # Add before current approver
                if self.add_approver:
                    setting_line_obj = self.env['document.internal.main.setting.line'].search([
                        ('id', '=', int(self.setting_line))
                    ], limit=1)
                    for aa in self.add_approver:
                        sequence_count += 1
                        self.env['document.internal.main.setting.line'].create(
                            {
                                'setting_id': int(self.setting_id),
                                'employee_id': aa.id,
                                'job_id_name': aa.job_id.id,
                                'step': setting_line_obj.step,
                                'status': setting_line_obj.status,
                                'approve_type': 'comments',
                                'status_approve': '0',
                                'is_active': True,
                                'sequence': sequence_count
                            }
                        )
                    sequence_count += 1
                    setting_line_obj.write({
                        'is_active': True,
                        'sequence': sequence_count
                    })
                # Add after current approver
                if self.change_approver:
                    setting_line_obj = self.env['document.internal.main.setting.line'].search([
                        ('id', '=', int(self.setting_line))
                    ], limit=1)
                    setting_line_obj.write({
                        'is_active': False,
                        'status_approve': '',
                        'sequence': sequence_count
                    })
                    for ca in self.change_approver:
                        sequence_count += 1
                        self.env['document.internal.main.setting.line'].create(
                            {
                                'setting_id': int(self.setting_id),
                                'employee_id': ca.id,
                                'job_id_name': ca.job_id.id,
                                'step': setting_line_obj.step,
                                'status': setting_line_obj.status,
                                'approve_type': 'require',
                                'status_approve': '0',
                                'is_active': True,
                                'sequence': sequence_count
                            }
                        )
            else:
                setting_line.write({
                  'sequence': sequence_count,
                })
            sequence_count += 1

        return {'type': 'ir.actions.act_window_close'}

    # @api.multi
    # def close_wizard(self):
    #     return {'type': 'ir.actions.act_window_close'}