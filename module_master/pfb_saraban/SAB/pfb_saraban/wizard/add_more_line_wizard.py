from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class AddLineWizard(models.TransientModel):
    _name = "add.line.wizard.receive"
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
    memo = fields.Text('Memo', required=True)

    total_for_approve = fields.Integer(
        string="Total For Approval", readonly=True)
    setting_id = fields.Char('Id setting')
    setting_line = fields.Char('Id setting line')
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผอ.ฝ่าย'),
        ('2', 'ฝ่ายที่เกี่ยวข้อง')
    ])

    @api.multi
    def action_approve(self):
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
