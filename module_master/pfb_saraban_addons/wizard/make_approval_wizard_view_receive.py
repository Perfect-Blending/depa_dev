# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class MakeApprovalWizardReceiveInherit(models.TransientModel):
    _inherit = "make.approval.wizard.receive"

    memo = fields.Html(
        'Memo',
        required=True,
        default='',
    )
    to_approver = fields.Many2many(
        'hr.employee',
        'to_approver_employee_rel',
        'to_approver_id',
        'employee_id',
        string='To',
        index=True
    )
    add_approver = fields.Many2many(
        'hr.employee',
        'add_approver_employee_rel',
        'add_approver_id',
        'employee_id',
        string='Add Approver',
        index=True
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
        readonly='1',
    )
    is_add = fields.Boolean(
        string='Add',
        default=True,
    )
    order_choices = fields.Many2many(
        'order.choices',
        string='Order',
        # default='please_consider',
    )

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
        # if setting_line_check_rights.step != '1':
        #     raise UserError('Can not add approver on this step')
        for setting_line in setting_line_obj:
            if setting_line.id == int(self.setting_line):
                if self.to_approver or self.add_approver:
                    setting_line_obj = self.env['receive.document.main.setting.lines'].search([
                        ('id', '=', int(self.setting_line))
                    ], limit=1)
                    sequence_count += 1
                    setting_line_obj.write({
                        'is_active': True,
                        'sequence': sequence_count
                    })
                if self.to_approver:
                    for ta in self.to_approver:
                        self.env['receive.document.main.setting.lines'].create(
                            {
                                'setting_id': int(self.setting_id),
                                'employee_id': ta.id,
                                'to_or_cc': 'to',
                                'order_choices': [(6, 0, [choice.id for choice in self.order_choices])],
                                'job_id_name': ta.job_id.id,
                                'step': '2',
                                'status': setting_line_obj.status,
                                'approve_type': 'comments',
                                'status_approve': '0',
                                'is_active': True,
                                'sequence': sequence_count
                            }
                        )
                        sequence_count += 1
                        self.env['waiting.receive.document.main.setting.lines'].create(
                                {
                                    'setting_id': int(self.setting_id),
                                    'employee_id': ta.id,
                                }
                        )

                if self.add_approver:
                    for aa in self.add_approver:
                        self.env['receive.document.main.setting.lines'].create(
                            {
                                'setting_id': int(self.setting_id),
                                'employee_id': aa.id,
                                'to_or_cc': 'cc',
                                'order_choices': [(6, 0, [choice.id for choice in self.order_choices])],
                                'job_id_name': aa.job_id.id,
                                'step': '2',
                                'status': setting_line_obj.status,
                                'approve_type': 'comments',
                                'status_approve': '0',
                                'is_active': True,
                                'sequence': sequence_count
                            }
                        )
                        sequence_count += 1
                        self.env['waiting.receive.document.main.setting.lines'].create(
                                {
                                    'setting_id': int(self.setting_id),
                                    'employee_id': aa.id,
                                }
                        )
            else:
                setting_line.write({
                    'sequence': sequence_count,
                })
            sequence_count += 1

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_approve(self):
        if self.memo == "<p><br></p>":
            raise UserError('Memo can not be empty')
        if self.add_approver or self.to_approver:
            self.save_approver_button()
        res = super(MakeApprovalWizardReceiveInherit, self).action_approve()
        return res


class OrderChoices(models.Model):
    _name = 'order.choices'

    name = fields.Char(
        string='Name',
        required=True,
    )
