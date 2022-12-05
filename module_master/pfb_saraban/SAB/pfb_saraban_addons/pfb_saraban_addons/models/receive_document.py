from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime


class receiveDocumentInherit(models.Model):
    _inherit = 'receive.document.main'


    show_receive_document = fields.Boolean(
        string='show_receive_document',
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_receive_document = self.env['receive.document.main']
        env_receive_document_approver = self.env['receive.document.main.setting.lines']
        params = self._context.get('params')

        res = super(receiveDocumentInherit, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )

        receive_document_list = env_receive_document.search([])
        for idl in receive_document_list:
            receive_document_user = []
            receive_document_obj = env_receive_document.search([('id', '=', idl.id)])
            if receive_document_obj.state != 'cancel':
                receive_document_user_obj = env_receive_document_approver.search([
                    ('setting_id', '=', idl.id),
                    ('is_active', '=', True)
                ])
                for rduo in receive_document_user_obj:
                    if not rduo.approve_time and rduo.is_active and rduo.status_approve == '0':
                        receive_document_user.append(rduo.employee_id.user_id.id)
                # receive_document_obj.show_receive_document = True

            if self._uid in receive_document_user:
                if not receive_document_obj.show_receive_document:
                    receive_document_obj.show_receive_document = True
            else:
                if receive_document_obj.show_receive_document:
                    receive_document_obj.show_receive_document = False

        return res

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
                        }
                    }
            raise ValidationError(_('Not your turn'))