from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning, RedirectWarning


class receiveDocumentInherit(models.Model):
    _inherit = 'receive.document.main'

    # show_receive_document = fields.Boolean(
    #     string='show_receive_document',
    # )
    refer_already_used = fields.Boolean(
        string='Refer already used',
    )
    # send_with_original_document = fields.Boolean(
    #     string='Sent with original document',
    #     default=False,
    # )

    # @api.model
    # def create(self, vals):
    #     doc_obj = self.env['receive.document.main'].search([
    #         ('from_document', '=', self.from_document),
    #         ('from_document', '!=', ''),
    #     ], limit=1)
    #     if doc_obj:
    #         if self.refer == doc_obj.refer:
    #             raise UserError('Refer already used')
    #     res = super(receiveDocumentInherit, self).create(vals)
    #     return res
    #
    #
    # @api.multi
    # def write(self, vals):
    #     doc_obj = self.env['receive.document.main'].search([
    #         ('from_document', '=', self.from_document),
    #         ('from_document', '!=', ''),
    #     ], limit=1)
    #     if doc_obj:
    #         if self.refer == doc_obj.refer:
    #             raise UserError('Refer already used')
    #     res = super(receiveDocumentInherit, self).write(vals)
    #     return res

    @api.multi
    @api.onchange('refer')
    def _onchange_from_document(self):
        if self.refer:
            doc_obj = self.env['receive.document.main'].search([
                ('refer', '=', self.refer),
                ('refer', '!=', ''),
            ])
            self.refer_already_used = False
            if doc_obj:
                for do in doc_obj:
                    if self.refer == do.refer:
                        self.refer_already_used = True
                        return {"warning": {"title": "Warning", "message": "Refer already used"}}

    @api.model
    def create(self, vals):
        vals['refer_already_used'] = False
        res = super(receiveDocumentInherit, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        vals['refer_already_used'] = False
        res = super(receiveDocumentInherit, self).write(vals)
        return res


    # @api.one
    # @api.constrains('from_document', 'refer')
    # def _check_from_document_name(self):
    #     if self.from_document != '':
    #         doc_obj = self.env['receive.document.main'].search([
    #             ('from_document', '=', self.from_document),
    #         ], limit=1)
    #         if doc_obj:
    #             if self.refer == doc_obj.refer:
    #                 raise ValidationError(_('Refer already used'))

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     env_receive_document = self.env['receive.document.main']
    #     env_receive_document_approver = self.env['receive.document.main.setting.lines']
    #     params = self._context.get('params')
    #
    #     res = super(receiveDocumentInherit, self).fields_view_get(
    #         view_id=view_id,
    #         view_type=view_type,
    #         toolbar=toolbar,
    #         submenu=submenu
    #     )
    #
    #     receive_document_list = env_receive_document.search([])
    #     for idl in receive_document_list:
    #         receive_document_user = []
    #         receive_document_obj = env_receive_document.search([('id', '=', idl.id)])
    #         if receive_document_obj.state != 'cancel':
    #             receive_document_user_obj = env_receive_document_approver.search([
    #                 ('setting_id', '=', idl.id),
    #                 ('is_active', '=', True)
    #             ])
    #             for rduo in receive_document_user_obj:
    #                 if not rduo.approve_time and rduo.is_active and rduo.status_approve == '0':
    #                     receive_document_user.append(rduo.employee_id.user_id.id)
    #             # receive_document_obj.show_receive_document = True
    #
    #         if self._uid in receive_document_user:
    #             if not receive_document_obj.show_receive_document:
    #                 receive_document_obj.show_receive_document = True
    #         else:
    #             if receive_document_obj.show_receive_document:
    #                 receive_document_obj.show_receive_document = False
    #     self._cr.commit()
    #     return res

    def action_make_approval_wizard(self):
        self.ensure_one()
        approve_type = False
        employee_id = False
        setting_line = False
        status = False
        count_nonactive = 0
        for line in self.setting_line_ids:
            if not line.is_active:
                count_nonactive += 1
        if self.setting_line_ids:
            state=0
            if(self.state=='sent'):
                state=1
            else:
                state=int(self.state)
            for line in self.setting_line_ids:
                if not line.approve_time and line.is_active and self.env.uid == line.employee_id.user_id.id and line.status_approve == '0' and line.step == str(state):
                    approve_type = line.approve_type
                    employee_id = line.employee_id
                    setting_line = line.id
                    status = line.status
                    step = line.step
                    return {
                        'name': "Make Approval Wizard",
                        'view_mode': 'form',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'make.approval.wizard.receive',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_approve_type': approve_type,
                            'default_employee_id': employee_id.id,
                            'default_setting_line': setting_line,
                            'default_status': status,
                            'default_total_for_approve': len(self.setting_line_ids)-count_nonactive,
                            'default_setting_id': self.id,
                            'default_material': self.material,
                        }
                    }
            raise ValidationError(_('Not your turn'))


    def receive_run_check(self):
        document_obj = self.env['receive.document.main'].search([])
        for do in document_obj:
            if do.speed == 'normal':
                do.speed = '1'
            if do.speed == 'express':
                do.speed = '2'
            if do.speed == 'urgent':
                do.speed = '3'
            if do.speed == 'vurgent':
                do.speed = '4'

    def internal_run_check(self):
        document_obj = self.env['document.internal.main'].search([])
        for do in document_obj:
            if do.speed == 'normal':
                do.speed = '1'
            if do.speed == 'express':
                do.speed = '2'
            if do.speed == 'urgent':
                do.speed = '3'
            if do.speed == 'vurgent':
                do.speed = '4'


class SettingLineExternalInherit(models.Model):
    _inherit = 'receive.document.main.setting.lines'

    order_choices = fields.Many2many(
        'order.choices',
        'order_choice_receive_rel',
        'receive_id',
        'order_choices_id',
        string='Order',
    )

    @api.onchange('employee_id')
    @api.multi
    def _onchange_employee_id(self):
        for line in self:
            line.job_id_name = line.employee_id.job_id.id
