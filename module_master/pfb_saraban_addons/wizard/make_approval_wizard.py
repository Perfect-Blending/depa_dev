# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)
add_approver_selected = []
change_approver_selected = []

add_group_selected = []
change_group_selected = []

class MakeApprovalWizardInherit(models.TransientModel):
    _inherit = "make.approval.wizard"

    memo = fields.Html(
        'Memo',
        required=True,
        default='',
    )
    change_approver_groups = fields.Many2many(
        'document.employee.groups',
        'change_approver_group_rel',
        'approval_id',
        'group_id',
        string='Change Approver Group',
        index=True
    )
    change_approver = fields.Many2many(
        'hr.employee',
        'change_approver_rel',
        'approval_id',
        'employee_id',
        string='Change Approver',
        index=True
    )
    # change_approver_selected = fields.Char()
    add_approver_groups = fields.Many2many(
        'document.employee.groups',
        'add_approver_group_rel',
        'approval_id',
        'group_id',
        string='Add Approver Group',
        index=True
    )
    add_approver = fields.Many2many(
        'hr.employee',
        'add_approver_rel',
        'approval_id',
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
    is_add_or_change = fields.Boolean(
        string='Add Or Change',
        default=False,

    )
    favorite_add = fields.Boolean(
        string='+ Favorite',
        default=False,
    )
    favorite_change = fields.Boolean(
        string='+ Favorite',
        default=False,
    )

    favorite_add_discard_button = fields.Boolean('Discard')
    action_favorite_add_button = fields.Boolean(
        string='Approve',
        default=False,
    )
    favorite_change_discard_button = fields.Boolean('Discard')
    action_favorite_change_button = fields.Boolean(
        string='Approve',
        default=False,
    )
    group_name_add = fields.Char('Add Approver Group Name')
    group_name_change = fields.Char('Change Approver Group Name')
    # @api.multi
    # @api.onchange(
    #     'change_approver',
    #     'add_approver',
    # )

    @api.onchange('favorite_add_discard_button')
    def favorite_add_discard(self):
        self.favorite_add = False

    @api.onchange('favorite_change_discard_button')
    def favorite_change_discard(self):
        self.favorite_change = False

    @api.onchange('action_favorite_change_button')
    def action_change_favorite(self):

        change_approver_array = [aa.id for aa in self.change_approver]

        # print(add_approver_array)
        if change_approver_array != []:
            if not self.group_name_change:
                raise ValidationError(_('field group name is required'))

            if self.group_name_change:
                employee_group_obj = self.env['document.employee.groups'].create({
                'group_name': self.group_name_change,
                'flag': False,
                'hr_employee_ids': [(6, 0, change_approver_array)]
                })
                #print(change_approver_array)
            self.favorite_change = False
            if employee_group_obj:
                self.change_approver_groups = [(6, 0, [employee_group_obj.id])]
                self.change_approver = [(6, 0, change_approver_array)]
                self.group_name_change = ''


    @api.onchange('action_favorite_add_button')
    def action_add_favorite(self):
        add_approver_array = [aa.id for aa in self.add_approver]

       # print(add_approver_array)
        if add_approver_array != []:
            if not self.group_name_add:
                raise ValidationError(_('field group name is required'))
            if self.group_name_add:
                employee_group_obj = self.env['document.employee.groups'].create({
                'group_name': self.group_name_add,
                'flag': False,
                'hr_employee_ids': [(6, 0, add_approver_array)]
                })
            #print(add_approver_array)
            self.favorite_add = False
            if employee_group_obj:
                self.add_approver_groups = [(6, 0, [employee_group_obj.id])]
                self.add_approver = [(6, 0, add_approver_array)]
                self.group_name_add = ''

    @api.multi
    @api.onchange(
        'change_approver',
        'add_approver'
    )
    def _onchange_approver(self):
        for record in self:
            if record.change_approver or record.add_approver:
                record.is_approver_change = True

    @api.onchange('add_approver_groups')
    def _onchange_add_approver_groups(self):
        # print(self)
        global add_group_selected
        groups = []
        emps = []
        emps_selected = [employee.id for employee in self.add_approver]

        for group in self.add_approver_groups:
            groups.append(group.id)
            for employee in group.hr_employee_ids:
                emps.append(employee.id)

        if len(groups) > len(add_group_selected):
            if len(emps) > len(emps_selected):
                group_selected = list(set(groups) - set(add_group_selected))
                if len(group_selected) >= 1:
                    group_added = self.env['document.employee.groups'].search([
                        ('id', '=', group_selected[0])
                    ])
                    emps_added = [gadd.id for gadd in group_added.hr_employee_ids]
                    emps_selected = emps_selected + emps_added
            else:
                emps_selected = emps_selected + emps
        else:
            group_deselected = list(set(add_group_selected) - set(groups))
            if len(group_deselected) >= 1:
                group_removed = self.env['document.employee.groups'].search([
                    ('id', '=', group_deselected[0])
                ])
                emps_removed = [grm.id for grm in group_removed.hr_employee_ids]
                emps_selected = list(set(emps_selected) - set(emps_removed))

        add_group_selected = groups
        self.add_approver = [(6, 0, emps_selected)]

    @api.onchange('change_approver_groups')
    def _onchange_approver_groups(self):
        # print(self)
        global change_group_selected
        groups = []
        emps = []
        emps_selected = [employee.id for employee in self.change_approver]

        for group in self.change_approver_groups:
            groups.append(group.id)
            for employee in group.hr_employee_ids:
                emps.append(employee.id)

        if len(groups) > len(change_group_selected):
            if len(emps) > len(emps_selected):
                group_selected = list(set(groups) - set(change_group_selected) )
                if len(group_selected) >= 1:
                    group_added = self.env['document.employee.groups'].search([
                        ('id', '=', group_selected[0])
                    ])
                    emps_added = [gadd.id for gadd in group_added.hr_employee_ids]
                    emps_selected = emps_selected + emps_added
            else:
                emps_selected = emps_selected + emps
        else:
            group_deselected = list(set(change_group_selected) - set(groups))
            if len(group_deselected) >= 1:
                group_removed = self.env['document.employee.groups'].search([
                    ('id', '=', group_deselected[0])
                ])
                emps_removed = [grm.id for grm in group_removed.hr_employee_ids]
                emps_selected = list(set(emps_selected) - set(emps_removed))

        change_group_selected = groups
        self.change_approver = [(6, 0, emps_selected)]

        # temp = []
        # global change_approver_selected
        #
        # for group in self.change_approver_groups:
        #     for employee in group.hr_employee_ids:
        #         temp.append(employee.id)
        #
        # print({"temp" : temp})
        # if len(temp) > len(change_approver_selected):
        #     change_approver_selected = temp
        # else:
        #     selected = [employee.id for employee in self.change_approver]
        #     unselected = list(set(selected) - set(temp))
        #     change_approver_selected = list(set(selected) - set(unselected))
        #
        # self.change_approver = [(6, 0, change_approver_selected)]
        #
        # print({"change_approver_selected" : change_approver_selected})


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
                        self.env['waiting.document.main.setting.line'].create(
                            {
                                'setting_id': int(self.setting_id),
                                'employee_id': aa.id,
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
                        self.env['waiting.document.main.setting.line'].create(
                                {
                                    'setting_id': int(self.setting_id),
                                    'employee_id': ca.id,
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

    def action_color_text(self,setting_id,setting_line_id):
        cr = self.env.cr
        # ถ้าไม่ใช่ขั้นตอนเเรกให้หาว่าขั้นตอนก่อนหน้าเป็นอะไร เอาวันที่ max สุดมาใส่
        # หา Step ที่น้อยกว่าปัจจุบัน
        WHERE = " setting_id = %s" % self.setting_id
        WHERE += " AND step < '%s' " % setting_line_id.step
        sql = (''' select DATE(approve_time) as approve_time from document_internal_main_setting_line  WHERE %s order by approve_time desc limit 1  ''') % WHERE
        cr.execute(sql)
        row = cr.dictfetchone()
        # print(row)
        if not row:
            # step แรกสุด
            setting_line_id.update({
                'max_date_approve': setting_id.date_document,
            })
            print('step--->1')
        else:
            print('step---> ')
            setting_line_id.update({
                'max_date_approve': row.get('approve_time')
            })
        # raise ValidationError(setting_line_id.step)
        return True

    # self.action_color_text(setting_id, setting_line_id)
    @api.multi
    def action_approve(self):
        if self.memo == "<p><br></p>":
            raise UserError('Memo can not be empty')
        try:
            if not self.memo:
                raise ValidationError(_('field memo is required'))
            if self.env.uid == self.employee_id.user_id.id:
                setting_line_id = self.env['document.internal.main.setting.line'].browse(
                    int(self.setting_line))
                setting_id = self.env['document.internal.main'].browse(
                    int(self.setting_id))
                state = setting_id.state
                count = 0
                check_full_step_comment = True
                comment_count = 0
                states = []
                next_state = ''
                for setting_line in setting_id.setting_line_ids:
                    if setting_line.status == self.status and setting_line.approve_type == 'require':
                        check_full_step_comment = False
                        break
                approval_count = 0
                self.action_color_text(setting_id, setting_line_id)
                setting_id.update({
                    'approval_count': setting_id.approval_count + 1,
                })
                if setting_line_id.approve_type == 'require':
                    setting_line_id.update({
                        'approve_time': datetime.today(),
                        'comment': self.memo,
                        'status_approve': '1',
                    })
                else:
                    setting_line_id.update({
                        'approve_time': datetime.today(),
                        'comment': self.memo,
                        'status_approve': '2',
                    })
                for setting_line in setting_id.setting_line_ids:
                    if setting_line.status_approve == '0' and setting_line.approve_type == 'require':
                        count += 1
                    if setting_line.status_approve == '0' and setting_line.approve_type == 'comments' and check_full_step_comment:
                        comment_count += 1
                        # print(comment_count)

                if (count == 0 and comment_count == 0):
                    for setting_line in setting_id.setting_line_ids:
                        if setting_line.status_approve == '0' and setting_line.approve_type == 'comments' and not setting_line.comment and setting_line.is_active == True:
                            setting_line.status_approve = ''
                            setting_id.approval_count += 1
                    state = setting_line_id.step
                    for setting_line in setting_id.setting_line_ids:
                        if setting_line.is_active == True:
                            states.append(setting_line.step)
                    # Get next state
                    for state_all in sorted(states):
                        if (state_all > state):
                            next_state = state_all
                            # raise ValidationError(_(next_state))
                            break
                    for setting_line in setting_id.setting_line_ids:
                        if (setting_line.step == next_state and setting_line.is_active == True):
                            setting_line.status_approve = '0'
                # raise ValidationError(_(count))
                sequence_id = False
                if (setting_id.approval_count) == self.total_for_approve:
                    # raise ValidationError(_(setting_id.document_type))
                    # if setting_id.document_type!='บันทึกข้อความ':
                    #     raise ValidationError(_('True'))

                    #ISSUE 283
                    if setting_id.document_type == 'หนังสือรับรอง':
                        setting_id.document_type = 'หนังสือภายนอก+หนังสือรับรอง'

                    if setting_id.document_type not in ['บันทึกข้อความ', 'หนังสือภายนอก+หนังสือรับรอง']:
                        if setting_id.document_type in ['คำสั่ง ก', 'คำสั่ง ข', 'คำสั่ง ค', 'คำสั่ง พ', 'ประกาศ', 'ประกาศพัสดุ',
                                                        'ข้อบังคับ', 'ระเบียบ']:
                            if setting_id.name_real in ['', ' ', None, False]:
                                sequence_id = self.env['ir.sequence'].search([
                                    ('document_type', '=', setting_id.document_type),
                                    ('sarabun_active', '=', True)
                                ])
                            if sequence_id:
                                setting_id.update({
                                    'name_real': sequence_id.next_by_id(),
                                    'date_document_real': fields.Date.today()
                                })
                            else:
                                raise ValidationError(
                                    _('Please add the sequence ' + setting_id.document_type))
                        else:
                            if setting_id.name_real in ['', ' ', None, False]:
                                sequence_id = False
                                sequence_id = self.env['ir.sequence'].search([
                                    ('department_id', '=',
                                     setting_id.department_id.id),
                                    ('document_type', '=',
                                     setting_id.document_type),
                                    ('sarabun_active', '=', True)
                                ])
                            if sequence_id and sequence_id.sarabun_active:
                                setting_id.update({
                                    'name_real': sequence_id.next_by_id(),
                                    'date_document_real': fields.Date.today()
                                })
                            else:
                                raise ValidationError(
                                    _('Please add the sequence ' + setting_id.document_type))

                    if setting_id.document_type == 'หนังสือภายนอก+หนังสือรับรอง':
                        if setting_id.name_real in ['', ' ', None, False]:
                            sequence_id = setting_id.env['ir.sequence'].search([
                                ('document_type', '=', setting_id.document_type),
                                ('sarabun_active', '=', True)
                            ]) or False
                            if sequence_id:
                                nextnumber = setting_id.prefix + " " + sequence_id.next_by_id()
                                setting_id.update({
                                    'name_real': nextnumber,
                                    'date_document_real': fields.Date.today()
                                })
                            else:
                                raise ValidationError(
                                    _('Please add the sequence'))
                    setting_id.update({
                        'state': 'done',
                    })
                else:
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
                    if line_id.is_active and line_id.status_approve == '0':
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