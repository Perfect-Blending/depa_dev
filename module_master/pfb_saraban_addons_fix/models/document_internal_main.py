from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DocumentInternalMainFix(models.Model):
    _inherit = 'document.internal.main'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    material = fields.Text(string='Material', track_visibility='onchange', )
    is_check_approval = fields.Binary(compute='_compute_check_approval')
    is_attachment_approval = fields.Binary(compute='_compute_attachment_approval')

    next_approval_id = fields.Char(string='Next Approval')
    next_approval_ids = fields.Char(compute='_compute_next_approval', )
    next_approval_user_ids = fields.Many2many('hr.employee',
                                              string='Next Approval Users',
                                              relation="document_internal_main_hr_employee_rel",
                                              column1='document_internal_main_id',
                                              column2='hr_employee_id',
                                              compute='_compute_next_approval')
    can_approve = fields.Boolean()
    next_comment_ids = fields.Char(compute='_compute_next_approval', )
    next_comment_user_ids = fields.Many2many('hr.employee',
                                             string='Next Approval Users',
                                             relation="document_internal_main_hr_employee_rel",
                                             column1='document_internal_main_id',
                                             column2='hr_employee_id',
                                             compute='_compute_next_approval')
    can_comment = fields.Boolean()

    @api.multi
    def _compute_next_approval(self):
        for document in self:
            status_th = ''
            step_line = []
            status_line = []
            employee_line = []
            comment_step = []
            comment_employee = []
            comment_status = []
            employee_id = []
            current = 0
            approval_ids_ready = document.setting_line_ids \
                .filtered(lambda app: app.is_active == True and app.status_approve != '1' and app.status_approve != '2'
                                      and app.approve_type == 'require')
            approval_comment_ready = document.setting_line_ids \
                .filtered(lambda app: app.is_active == True and app.status_approve != '1' and app.status_approve != '2'
                                      and app.approve_type == 'comments')
            print(approval_comment_ready)
            for line in document.setting_line_ids:
                if line.is_active and line.status_approve != '1' and line.status_approve != '2':
                    if line.status == '1':
                        status_th = 'ผอ.ฝ่าย'
                    if line.status == '2':
                        status_th = 'ฝ่ายที่เกี่ยวข้อง0'
                    if line.status == '3':
                        status_th = 'เลขา ชสศด./รสศด.'
                    if line.status == '4':
                        status_th = 'ชสศด.'
                    if line.status == '5':
                        status_th = 'รสศด.'
                    if line.status == '6':
                        status_th = 'ฝ่ายที่เกี่ยวข้อง-2'
                    if line.status == '7':
                        status_th = 'ผสศด.'
                    if line.status_approve == '0':
                        current = int(line.step)
                        print(current, int(line.step))
                    if line.approve_type == 'require':
                        step_line.append(line.step)
                        status_line.append(status_th)
                        employee_line.append(line.employee_id.name)
                    if line.approve_type == 'comments' and int(line.step) >= current:
                        print(int(line.step), current)
                        comment_step.append(line.step)
                        comment_status.append(status_th)
                        comment_employee.append(line.employee_id.name)
            if len(step_line) != 0:
                document.next_approval_ids = 'ขั้นตอน' + ' ' + step_line[0] + ' ' + status_line[0] + ' ' + \
                                             employee_line[0]
                document.next_approval_user_ids = approval_ids_ready.mapped('employee_id')
            if len(comment_step) != 0:
                document.next_comment_ids = 'ขั้นตอน' + ' ' + comment_step[0] + ' ' + comment_status[0] + ' ' + \
                                            comment_employee[0]
                document.next_comment_user_ids = approval_comment_ready.mapped('employee_id')

    @api.multi
    def action_reset_to_draft(self):

        if self.state != 'sent' and self._uid == self.create_uid:
            raise UserError(
                _('You cannot draft an document'))

        for rec in self:
            rec.write({'state': 'draft'})
        for approval in self.setting_line_ids:
            print(approval, 555555)
            approval.write({
                'approve_time': False,
                'comment': '',
                'status_approve': False,
            })

            values = []
            doc_id = approval.setting_id.id
            waiting_line = self.env['waiting.document.main.setting.line'].search([
                ('setting_id', '=', doc_id)
            ])
            waiting_line.unlink()
            if approval.is_active and approval.status_approve == '0':
                values.append([0, 0, {
                    'employee_id': approval.employee_id.id
                }])
                values.append([0, 0, {
                    'setting_id': approval.setting_id.id
                }])
            approval.setting_id.update({
                'waiting_line_ids': values
            })
            waiting_line_ids = self.env['waiting.document.main.setting.line'].search([
                ('setting_id', '=', doc_id), ('employee_id', '=', False)
            ])
            waiting_line_ids.unlink()
        return True

    @api.multi
    def _compute_check_approval(self):
        for rec in self:
            status = []
            for line_approval in rec.setting_line_ids:
                if line_approval.is_active:
                    status.append(line_approval.status_approve)
            if rec.setting_line_ids:
                if status[0] == '0' and rec.create_uid.name == rec.env.user.name:
                    rec.is_check_approval = True
                if status[0] != '0':
                    rec.is_check_approval = False

    @api.multi
    def _compute_attachment_approval(self):
        for rec in self:
            name_approval = []
            if rec.setting_line_ids:
                for line_approval in rec.setting_line_ids:
                    # if line_approval.is_active:
                    if rec.env.user.name == line_approval.employee_id.name:
                        rec.is_attachment_approval = True
                        return
                    else:
                        rec.is_attachment_approval = False
                #     name_approval.append(line_approval.employee_id.name)
                # print(name_approval)
                # if name_approval in rec.env.user.name:
                #     rec.is_attachment_approval = True
                # else:
                #     rec.is_attachment_approval = False
                print(rec.is_attachment_approval)

    @api.onchange('reference_line_ids_multi')
    def _onchange_partner_type(self):
        domain = {}
        if self.reference_line_ids_multi:
            doc = self.reference_line_ids_multi
            print(doc)
        print(domain)
        return domain

    # # log แนบไฟล์
    @api.multi
    def write(self, vals):
        rec = super(DocumentInternalMainFix, self).write(vals)
        for res in self.attachment_ids:
            if res.create_uid.id == self._uid and res.description != 'post':
                self.message_post(body='แนบไฟล์' + ' : ' + str(res.name))
                res.write({
                    'description': 'post',
                })
        return rec


class DocumentInternalMainLineFix(models.Model):
    _inherit = 'document.internal.main.setting.line'

    @api.multi
    def action_reset_approval(self):
        status = []
        step = []
        status_approve = []
        for approval in self:
            approval.write({
                'approve_time': False,
                'comment': '',
                'status_approve': '0',
            })

            values = []
            doc_id = approval.setting_id.id
            waiting_line = self.env['waiting.document.main.setting.line'].search([
                ('setting_id', '=', doc_id)
            ])
            waiting_line.unlink()
            if approval.is_active and approval.status_approve == '0':
                values.append([0, 0, {
                    'employee_id': approval.employee_id.id
                }])
                values.append([0, 0, {
                    'setting_id': approval.setting_id.id
                }])
            approval.setting_id.update({
                'waiting_line_ids': values
            })
            waiting_line_ids = self.env['waiting.document.main.setting.line'].search([
                ('setting_id', '=', doc_id), ('employee_id', '=', False)
            ])
            waiting_line_ids.unlink()
            count = 0
            for line_doc in approval.setting_id.setting_line_ids:

                if line_doc.status_approve == '1' or line_doc.status_approve == '2':
                    count += 1
                if line_doc.approve_time:
                    if line_doc.is_active:
                        status.append(line_doc.status)
                        status_approve.append(approval.status_approve)
                        status2 = ''
                        if status[-1] == '1':
                            print(line_doc.status_approve)
                            if line_doc.status_approve == '1':
                                status2 = '1'
                            if line_doc.status_approve == '0':
                                status2 = 'sent'
                        if status[-1] == '2':
                            status2 = '2'
                        if status[-1] == '3':
                            status2 = '3'
                        if status[-1] == '4':
                            status2 = '4'
                        if status[-1] == '5':
                            status2 = '5'
                        if status[-1] == '6':
                            status2 = '6'
                        if status[-1] == '7':
                            status2 = '6'
                        line_doc.setting_id.write({
                            'state': status2,
                        })
                        if status_approve[0] == '0':
                            step2 = approval.step
                            setting_id = self.env['document.internal.main'].browse(
                                int(self.setting_id))
                            for st in line_doc.setting_id.setting_line_ids:
                                if st.is_active:
                                    if step2 < st.step:
                                        print('test02')
                                        st.write({
                                            'approve_time': False,
                                            'comment': '',
                                            'status_approve': '',
                                        })
                else:
                    if line_doc.status == '1':
                        if line_doc.is_active:
                            status.append(line_doc.status)
                            status_approve.append(approval.status_approve)
                            status2 = 'sent'
                            line_doc.setting_id.write({
                                'state': status2,
                            })
                            if status_approve[0] == '0':
                                step2 = approval.step
                                for st in line_doc.setting_id.setting_line_ids:
                                    if st.is_active:
                                        if step2 < st.step:
                                            print('test02')
                                            st.write({
                                                'approve_time': False,
                                                'comment': '',
                                                'status_approve': '',
                                            })
            for count_approve in approval.setting_id:
                count_approve.approval_count = count

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class MakeApprovalWizardInherit(models.TransientModel):
    _inherit = "make.approval.wizard"

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

                    # unlink is_active = False
                    waiting_obj = self.env['waiting.document.main.setting.line'].search([
                        ('setting_id', '=', int(setting_line_obj.setting_id.id)),
                        ('employee_id', '=', int(setting_line_obj.employee_id.id))])
                    waiting_obj.unlink()

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
