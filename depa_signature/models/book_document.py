# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models
from odoo import tools, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class book_document(models.Model):
    _name = 'book_document'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    book_document_type = fields.Selection([
        ('คำสั่ง ก', 'คำสั่ง ก'),
        ('คำสั่ง ข', 'คำสั่ง ข'),
        ('คำสั่ง ค', 'คำสั่ง ค'),
        ('คำสั่ง พ', 'คำสั่ง พ'),
        ('ประกาศ', 'ประกาศ'),
        ('ข้อบังคับ', 'ข้อบังคับ'),
        ('หนังสือภายนอก+หนังสือรับรอง', 'หนังสือภายนอก+หนังสือรับรอง'),
        ('ระเบียบ', 'ระเบียบ'),
    ], string='Document type select', default='หนังสือภายนอก+หนังสือรับรอง')

    employee_id = fields.Many2one('hr.employee', string="ชื่อผู้จอง", default=_default_employee,
                                  required=True, ondelete='cascade', index=True, copy=False)
    department_id = fields.Many2one('hr.department', string="Department id",
                                    related="employee_id.department_id", readonly=True, copy=False)

    book_name_real = fields.Char(
        string="เลขหนังสือ"
    )

    book_date_document_real = fields.Date(
        string="วันที่จอง"
    )

    prefix = fields.Char(
        string='prefix',
        copy=True,
        store=True,
        related='department_id.depa_document_sequence',
    )


    def action_sent_book(self):
        # print(self.employee_id)

        if self.book_document_type not in ['บันทึกข้อความ', 'หนังสือภายนอก+หนังสือรับรอง']:
            if self.book_document_type in ['คำสั่ง ก', 'คำสั่ง ข', 'คำสั่ง ค', 'คำสั่ง พ', 'ประกาศ', 'ข้อบังคับ',
                                            'ระเบียบ']:
                sequence_id = self.env['ir.sequence'].search([
                    ('document_type', '=', self.book_document_type),
                    ('sarabun_active', '=', True)
                ])
                if sequence_id:
                    self.update({
                        'book_name_real': sequence_id.next_by_id(),
                        'book_date_document_real': fields.Date.today()
                    })
                else:
                    raise ValidationError(
                        _('Please add the sequence ' + self.book_document_type))
            else:

                sequence_id = self.env['ir.sequence'].search([
                    ('department_id', '=', self.department_id.id),
                    ('document_type', '=', self.book_document_type),
                    ('sarabun_active', '=', True)
                ])
                if sequence_id and sequence_id.sarabun_active:
                    self.update({
                        'book_name_real': sequence_id.next_by_id(),
                        'book_date_document_real': fields.Date.today()
                    })
                else:
                    raise ValidationError(
                        _('Please add the sequence ' + self.book_document_type))

        if self.book_document_type == 'หนังสือภายนอก+หนังสือรับรอง':
            if self.book_name_real in ['', ' ', None, False]:
                sequence_id = self.env['ir.sequence'].search([
                    ('document_type', '=', self.book_document_type),
                    ('sarabun_active', '=', True)
                ]) or False
                if sequence_id:
                    nextnumber = self.prefix + " " + sequence_id.next_by_id()
                    self.update({
                        'book_name_real': nextnumber,
                        'book_date_document_real': fields.Date.today()
                    })
                else:
                    raise ValidationError(
                        _('Please add the sequence'))
