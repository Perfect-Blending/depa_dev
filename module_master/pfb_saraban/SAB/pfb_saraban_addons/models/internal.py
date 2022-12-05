from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, date
import logging
import json
import base64
from io import BytesIO
from docx import Document
from docx.shared import Inches
import requests as r
_logger = logging.getLogger(__name__)


class internalDocumentInherit(models.Model):
    _inherit = 'document.internal.main'

    show_internal_document = fields.Boolean(
        string='show_internal_document',
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_internal_document = self.env['document.internal.main']
        env_internal_document_approver = self.env['document.internal.main.setting.line']
        params = self._context.get('params')

        res = super(internalDocumentInherit, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )

        internal_document_list = env_internal_document.search([])
        for idl in internal_document_list:
            internal_document_user = []
            internal_document_obj = env_internal_document.search([('id', '=', idl.id)])
            if internal_document_obj.state != 'cancel':
                internal_document_user_obj = env_internal_document_approver.search([
                    ('setting_id', '=', idl.id),
                    ('is_active', '=', True)
                ])
                for iduo in internal_document_user_obj:
                    if not iduo.approve_time and iduo.is_active and iduo.status_approve == '0':
                        internal_document_user.append( iduo.employee_id.user_id.id )
                # internal_document_obj.show_internal_document = True

            if self._uid in internal_document_user:
                if not internal_document_obj.show_internal_document:
                    internal_document_obj.show_internal_document = True
            else:
                if internal_document_obj.show_internal_document:
                    internal_document_obj.show_internal_document = False

        return res

    @api.model
    def create(self, vals):
        res = super(internalDocumentInherit, self).create(vals)
        if res.setting_line_ids:
            sequence = 0
            for slid in res.setting_line_ids:
                slid.update({"sequence": sequence})
                sequence += 1
        return res

    @api.multi
    def write(self, vals):
        res = super(internalDocumentInherit, self).write(vals)
        if self.setting_line_ids:
            sequence = 0
            for slid in self.setting_line_ids:
                slid.update({"sequence": sequence})
                sequence += 1
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
            for line in self.setting_line_ids:
                if not line.approve_time and line.is_active and self.env.uid == line.employee_id.user_id.id and line.status_approve == '0':
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
                        'res_model': 'make.approval.wizard',
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
