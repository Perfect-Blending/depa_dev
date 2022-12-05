# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class MakeApprovalWizard(models.TransientModel):
    _name = "make.approval.wizard.receive"
    _description = 'สารบรรณ หนังสือรับ'

    approve_type = fields.Selection(readonly=True, string="Approve type",
                                    selection=[
                                        ('comments', 'Comments only')
                                    ]
                                    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Approve User",
        readonly=True
    )
    memo = fields.Text('Memo')

    total_for_approve = fields.Integer(
        string="Total For Approval", readonly=True)
    setting_id = fields.Char('Id setting')
    setting_line = fields.Char('Id setting line')
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผอ.ฝ่าย'),
        ('2', 'ฝ่ายที่เกี่ยวข้อง')
    ])
    add_line=fields.Boolean(string="For show add more line" ,default=True)
    change_new=fields.Boolean(string="For show change line",default=False)
    setting_line_ids = fields.One2many('wizard.document.receive.main.setting.line',
                                       'setting_id', string='Document main line', require=True)
    step = fields.Selection(string="Step", selection=[
        ('1', '1'),
        ('2', '2'),
    ], compute='set_step')
    
    def set_step(self):
        setting_line_id = self.env['receive.document.main.setting.lines'].browse(
                    int(self.setting_line))
        self.step=setting_line_id.step
    @api.multi
    def action_add_index(self):
        # self.ensure_one()
        self.add_line=True
        self.change_new=False
        self.update({
                    'change_new': True,
                    'add_line':True
                })
        if len(list(self.setting_line_ids))>0:
            if self.env.uid == self.employee_id.user_id.id:
                setting_line_id = self.env['receive.document.main.setting.lines'].browse(
                    int(self.setting_line))
                setting_id = self.env['receive.document.main'].browse(
                    int(self.setting_id))
                main_line_ids = setting_id.setting_line_ids
                setting_id.setting_line_ids=False
                values = []
                for line_id in main_line_ids:
                    if self.setting_line!=str(line_id.id) :
                        print('line test'+str(line_id.id))
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id,
                            'job_id_name': line_id.job_id_name,
                            'status': line_id.status,
                            'step': line_id.step,
                            'approve_type': line_id.approve_type,
                            'approve_time':line_id.approve_time,
                            'comment':line_id.comment,
                            'status_approve':line_id.status_approve,
                            'is_active':line_id.is_active,
                        }])
                    else:
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id,
                            'job_id_name': line_id.job_id_name,
                            'status': line_id.status,
                            'step': line_id.step,
                            'approve_type': line_id.approve_type,
                            'approve_time':line_id.approve_time,
                            'comment':line_id.comment,
                            'status_approve':line_id.status_approve,
                            'is_active':True,
                        }])
                        for line in self.setting_line_ids:
                            values.append([0, 0, {
                            'employee_id': line.employee_id.id,
                            'job_id_name': line.job_id_name,
                            'status': self.step,
                            'step': self.step,
                            'approve_type': 'comments',
                            'status_approve':line_id.status_approve,
                            'is_active':True,
                        }])
                setting_id.update({
                'setting_line_ids': values
                })
                setting_id.update({
                'waiting_line_ids': False
                })
                main_line_ids = setting_id.setting_line_ids
                values = []
                for line_id in main_line_ids:
                    if line_id.is_active and line_id.status_approve=='0':
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id
                        }])
                setting_id.update({
                    'waiting_line_ids': values
                })
        else:
            raise ValidationError(_("Pleasw add line"))
                    
                
    @api.multi
    def action_change_employee(self):
        self.ensure_one()
        self.add_line=False
        self.change_new=True
        if len(list(self.setting_line_ids))>0:
            if self.env.uid == self.employee_id.user_id.id:
                setting_line_id = self.env['receive.document.main.setting.lines'].browse(
                    int(self.setting_line))
                setting_id = self.env['receive.document.main'].browse(
                    int(self.setting_id))
                main_line_ids = setting_id.setting_line_ids
                setting_id.setting_line_ids=False
                values = []
                for line_id in main_line_ids:
                    if self.setting_line!=str(line_id.id) :
                        print('line test'+str(line_id.id))
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id,
                            'job_id_name': line_id.job_id_name,
                            'status': line_id.status,
                            'step': line_id.step,
                            'approve_type': line_id.approve_type,
                            'approve_time':line_id.approve_time,
                            'comment':line_id.comment,
                            'status_approve':line_id.status_approve,
                            'is_active':line_id.is_active,
                        }])
                    else:
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id,
                            'job_id_name': line_id.job_id_name,
                            'status': line_id.status,
                            'step': line_id.step,
                            'approve_type': line_id.approve_type,
                            'approve_time':line_id.approve_time,
                            'comment':line_id.comment,
                            'status_approve':line_id.status_approve,
                            'is_active':False,
                        }])
                        for line in self.setting_line_ids:
                            values.append([0, 0, {
                            'employee_id': line.employee_id.id,
                            'job_id_name': line.job_id_name,
                            'status': self.step,
                            'step': self.step,
                            'approve_type': line_id.approve_type,
                            'status_approve':line_id.status_approve,
                            'is_active':True,
                        }])
                setting_id.update({
                'setting_line_ids': values
                })
                setting_id.update({
                'waiting_line_ids': False
                })
                main_line_ids = setting_id.setting_line_ids
                values = []
                for line_id in main_line_ids:
                    if line_id.is_active and line_id.status_approve=='0':
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id
                        }])
                setting_id.update({
                    'waiting_line_ids': values
                })
        else:
            raise ValidationError(_("Pleasw add line"))
                    
    @api.multi
    def save_line(self):
        if len(list(self.setting_line_ids))>0:
            if self.env.uid == self.employee_id.user_id.id:
                setting_line_id = self.env['receive.document.main.setting.lines'].browse(
                    int(self.setting_line))
                setting_id = self.env['receive.document.main'].browse(
                    int(self.setting_id))
                main_line_ids = setting_id.setting_line_ids
                setting_id.setting_line_ids=False
                values = []
                if(self.change_new):
                    
                    for line_id in main_line_ids:
                        if self.setting_line!=str(line_id.id) :
                            print('line test'+str(line_id.id))
                            values.append([0, 0, {
                                'employee_id': line_id.employee_id.id,
                                'job_id_name': line_id.job_id_name,
                                'status': line_id.status,
                                'step': line_id.step,
                                'approve_type': line_id.approve_type,
                                'approve_time':line_id.approve_time,
                                'comment':line_id.comment,
                                'status_approve':line_id.status_approve,
                                'is_active':line_id.is_active,
                            }])
                        else:
                            values.append([0, 0, {
                                'employee_id': line_id.employee_id.id,
                                'job_id_name': line_id.job_id_name,
                                'status': line_id.status,
                                'step': line_id.step,
                                'approve_type': line_id.approve_type,
                                'approve_time':line_id.approve_time,
                                'comment':line_id.comment,
                                'status_approve':line_id.status_approve,
                                'is_active':False,
                            }])
                            for line in self.setting_line_ids:
                                values.append([0, 0, {
                                'employee_id': line.employee_id.id,
                                'job_id_name': line.job_id_name,
                                'status': self.step,
                                'step': self.step,
                                'approve_type': line_id.approve_type,
                                'status_approve':line_id.status_approve,
                                'is_active':True,
                            }])
                    if(self.add_line):
                        for line_id in main_line_ids:
                            if self.setting_line!=str(line_id.id) :
                                print('line test'+str(line_id.id))
                                values.append([0, 0, {
                                    'employee_id': line_id.employee_id.id,
                                    'job_id_name': line_id.job_id_name,
                                    'status': line_id.status,
                                    'step': line_id.step,
                                    'approve_type': line_id.approve_type,
                                    'approve_time':line_id.approve_time,
                                    'comment':line_id.comment,
                                    'status_approve':line_id.status_approve,
                                    'is_active':line_id.is_active,
                                }])
                            else:
                                values.append([0, 0, {
                                    'employee_id': line_id.employee_id.id,
                                    'job_id_name': line_id.job_id_name,
                                    'status': line_id.status,
                                    'step': line_id.step,
                                    'approve_type': line_id.approve_type,
                                    'approve_time':line_id.approve_time,
                                    'comment':line_id.comment,
                                    'status_approve':line_id.status_approve,
                                    'is_active':False,
                                }])
                                for line in self.setting_line_ids:
                                    values.append([0, 0, {
                                    'employee_id': line.employee_id.id,
                                    'job_id_name': line.job_id_name,
                                    'status': self.step,
                                    'step': self.step,
                                    'approve_type': 'comments',
                                    'status_approve':line_id.status_approve,
                                    'is_active':True,
                                }])
                        
                setting_id.update({
                'setting_line_ids': values
                })
                setting_id.update({
                'waiting_line_ids': False
                })
                main_line_ids = setting_id.setting_line_ids
                values = []
                for line_id in main_line_ids:
                    if line_id.is_active and line_id.status_approve=='0':
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id
                        }])
                setting_id.update({
                    'waiting_line_ids': values
                })
        else:
            raise ValidationError(_("Pleasw add line"))
                    
    @api.multi
    def action_approve(self):
        # if not self.employee_id.dummy:
        #     raise ValidationError(_('Dummy not checked'))
        try:
            if self.env.uid == self.employee_id.user_id.id:
                setting_line_id = self.env['receive.document.main.setting.lines'].browse(
                    int(self.setting_line))
                setting_id = self.env['receive.document.main'].browse(
                    int(self.setting_id))
                state = setting_id.state
                count = 0
                states = []
                next_state = ''
                setting_id.update({
                    'approval_count': setting_id.approval_count + 1,
                })
                
                setting_line_id.update({
                    'approve_time': datetime.today(),
                    'comment': self.memo,
                    'status_approve': '1',
                })
                if(state=='sent'):
                    state='1'
                
                for setting_line in setting_id.setting_line_ids:
                    if setting_line.status_approve == '0' and state==setting_line.step and setting_line.is_active:
                        count+=1
                
                if(count == 0):
                    print("state change")
                    setting_id.message_post(body="state change")
                    for setting_line in setting_id.setting_line_ids:
                        states.append(setting_line.step)
                    # Get next state
                    for state_all in sorted(states):
                            if(state_all > state):
                                next_state = state_all
                                # raise ValidationError(_(next_state))
                                break
                    state=next_state
                    if(next_state==''):
                        state='done'
                        
                setting_id.update({
                    'state': state,
                })
                
                # setting_id.message_post(body="Has comment "+self.memo)
                setting_id.update({
                'waiting_line_ids': False
                })
                main_line_ids = setting_id.setting_line_ids
                values = []
                for line_id in main_line_ids:
                    if line_id.is_active and line_id.status_approve=='0':
                        values.append([0, 0, {
                            'employee_id': line_id.employee_id.id
                        }])
                setting_id.update({
                    'waiting_line_ids': values
                })
            else:
                raise ValidationError(
                    _('ชื่อผู้ใช้งานไม่มีสิทธิ์ในการอนุมัติ'))

            return True
        except Exception as e:
            raise ValidationError(_(e))
class WizardReceiveDocumentSettingLine(models.TransientModel):
    _name = 'wizard.document.receive.main.setting.line'
    _order = 'sequence'
    _description = 'สารบรรณ หนังสือภายใน บันทึกข้อความ'

    setting_id = fields.Many2one(
        "make.approval.wizard.receive", string="make approval wizard")
    # test= fields.Char(related='setting_id.step')
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    job_id_name = fields.Many2one('hr.job', string="Job name")
    """Step and state are the same so don have to do anything about it"""
    dummy = fields.Boolean(
        string="dummy", related='employee_id.dummy', readonly=True)
    
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(string='Sequence', index=True)