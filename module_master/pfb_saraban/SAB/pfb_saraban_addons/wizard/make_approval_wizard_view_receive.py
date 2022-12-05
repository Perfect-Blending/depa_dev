# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class MakeApprovalWizardReceiveInherit(models.TransientModel):
    _inherit = "make.approval.wizard.receive"

    memo = fields.Text('Memo', required=False)
    add_approver = fields.Many2many(
        'hr.employee',
        string='Add Approver'
    )
    save_approver_button = fields.Boolean(
        default=False,
    )

    is_approver_change = fields.Boolean(
        default=False,
        compute='_onchange_approver',
    )

    material = fields.Text(
        string='Material',
        compute='_get_note',
    )

    show_material = fields.Boolean(
        default=False,
        compute='_show_note',
    )


    @api.multi
    def _show_note(self):
        setting_line_check_rights = self.env['receive.document.main.setting.lines'].search([
            ('id', '=', int(self.setting_line))
        ], limit=1)
        if setting_line_check_rights.step == '1':
            self.show_material = True


    @api.multi
    def _get_note(self):
        setting_obj = self.env['receive.document.main'].search([
            ('id', '=', int(self.setting_id))
        ], limit=1, order='id')
        if setting_obj.material:
            self.material = setting_obj.material


    @api.multi
    @api.onchange(
        'add_approver'
    )
    def _onchange_approver(self):
        for record in self:
            if record.add_approver:
                record.is_approver_change = True

    @api.multi
    # @api.onchange('save_approver_button')
    def save_approver_button(self):
        sequence_count = 0
        setting_obj = self.env['receive.document.main'].search([
            ('id', '=', int(self.setting_id))
        ], limit=1, order='id')
        setting_line_obj = self.env['receive.document.main.setting.lines'].search([
            ('setting_id', '=', int(self.setting_id))
        ], order='sequence')
        setting_line_check_rights = self.env['receive.document.main.setting.lines'].search([
            ('id', '=', int(self.setting_line))
        ], limit=1)
        if setting_line_check_rights.step != '2':
            raise UserError('Can not add approver on this step')
        for setting_line in setting_line_obj:
            if setting_line.id == int(self.setting_line):
                # Add before current approver
                if self.add_approver:
                    setting_line_obj = self.env['receive.document.main.setting.lines'].search([
                        ('id', '=', int(self.setting_line))
                    ], limit=1)
                    for aa in self.add_approver:
                        sequence_count += 1
                        self.env['receive.document.main.setting.lines'].create(
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
            else:
                setting_line.write({
                    'sequence': sequence_count,
                })
            sequence_count += 1

        return {'type': 'ir.actions.act_window_close'}