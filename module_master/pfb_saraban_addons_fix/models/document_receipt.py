from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DocumentReceiptInherit(models.Model):
    _inherit = 'receive.document.main'

    @api.multi
    def action_reset_to_draft(self):
        if self.state != 'sent' and self._uid == self.create_uid:
            raise UserError(
                _('You cannot draft an document'))

        for rec in self:
            rec.write({'state': 'draft'})
        return True

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
                .filtered(lambda app: app.is_active == True and app.status_approve != '1'
                                      and app.approve_type == 'require')
            approval_comment_ready = document.setting_line_ids \
                .filtered(lambda app: app.is_active == True and app.status_approve != '1'
                                      and app.approve_type == 'comments')
            print(approval_comment_ready)
            for line in document.setting_line_ids:
                if line.is_active and line.status_approve != '1':
                    if line.status == '1':
                        status_th = 'ผอ.ฝ่าย'
                    if line.status == '2':
                        status_th = 'ฝ่ายที่เกี่ยวข้อง-1'
                    if line.status == '3':
                        status_th = 'ชสศด.'
                    if line.status == '4':
                        status_th = 'รสศด.'
                    if line.status == '5':
                        status_th = 'ฝ่ายที่เกี่ยวข้อง-2'
                    if line.status == '6':
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
    def _compute_check_approval(self):
        for rec in self:
            status = []
            for line_approval in rec.setting_line_ids:
                if line_approval.is_active:
                    status.append(line_approval.status_approve)
            print(status)
            if rec.setting_line_ids:
                if status[0] == '0' and rec.create_uid.name == rec.env.user.name:
                    rec.is_check_approval = True
                if status[0] != '0':
                    rec.is_check_approval = False
                print(rec.is_check_approval, 55555)

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

    # @api.multi
    # def write(self, vals):
    #     rec = super(DocumentReceiptInherit, self).write(vals)
    #     waiting_line = self.env['waiting.receive.document.main.setting.lines'].search([
    #         ('setting_id', '=', self.id),
    #     ])
    #     employee = ''
    #     # if self.state == 'sent':
    #     for res in self:
    #         for re in res.setting_line_ids:
    #             print(re)
    #
    #     #         if res.status_approve == '0':
    #     #             employee = res.employee_id.id
    #     #     for del_wait in waiting_line:
    #     #         if del_wait.employee_id.id != employee:
    #     #             del_wait.unlink()
    #     return rec


class ReceiveDocumentInternalMainLineFix(models.Model):
    _inherit = 'receive.document.main.setting.lines'

    @api.multi
    def action_reset_approval(self):
        status = []
        step = []
        status_approve = []
        for approval in self:
            if approval.is_active:
                approval.write({
                    'approve_time': False,
                    'comment': '',
                    'status_approve': '0',
                })
            else:
                approval.write({
                    'approve_time': False,
                    'comment': '',
                    'status_approve': '',
                })
                doc_id = approval.setting_id.id
                employee = approval.employee_id.id
                waiting_line2 = self.env['waiting.receive.document.main.setting.lines'].search([
                    ('setting_id', '=', doc_id), ('employee_id', '=', employee)
                ])
                waiting_line2.unlink()
            values = []
            doc_id = approval.setting_id.id
            employee = approval.employee_id.id
            print(doc_id, employee)
            waiting_line = self.env['waiting.receive.document.main.setting.lines'].search([
                ('setting_id', '=', doc_id), ('employee_id', '=', False)
            ])
            waiting_line2 = self.env['waiting.receive.document.main.setting.lines'].search([
                ('setting_id', '=', doc_id), ('employee_id', '=', employee)
            ])
            waiting_line3 = self.env['waiting.receive.document.main.setting.lines'].search([
                ('setting_id', '=', doc_id)
            ])
            print(waiting_line3)
            group_wait = []
            for wait_re in waiting_line3:
                if wait_re.employee_id not in group_wait:
                    group_wait.append(wait_re)
                wait_re.unlink()

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
            # waiting_line_ids = self.env['waiting.receive.document.main.setting.lines'].search([
            #     ('setting_id', '=', doc_id), ('employee_id', '=', False)
            # ])
            # waiting_line_ids.unlink()
            if not approval.approve_time:
                if approval.is_active:
                    status.append(approval.status)
                    status_approve.append(approval.status_approve)
                    status2 = ''
                    if status[0] == '1':
                        status2 = '1'
                    if status[0] == '2':
                        status2 = '2'
                    if status[0] == 'done':
                        status2 = '2'
                    approval.setting_id.write({
                        'state': status2,
                    })
                    if status_approve[0] == '0':
                        step2 = approval.step
                        for st in approval.setting_id.setting_line_ids:
                            if st.is_active:
                                if step2 < st.step:
                                    st.write({
                                        'approve_time': False,
                                        'comment': '',
                                        'status_approve': '',
                                    })
                else:
                    if approval.status == '1':
                        if approval.is_active:
                            status.append(approval.status)
                            status_approve.append(approval.status_approve)
                            status2 = '1'
                            approval.setting_id.write({
                                'state': status2,
                            })
                            if status_approve[0] == '0':
                                step2 = approval.step
                                for st in approval.setting_id.setting_line_ids:
                                    if st.is_active:
                                        if step2 < st.step:
                                            st.write({
                                                'approve_time': False,
                                                'comment': '',
                                                'status_approve': '',
                                            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
