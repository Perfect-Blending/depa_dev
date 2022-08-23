# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class invoice_installment_inherit(models.Model):
    _inherit = 'account.invoice'

    def _get_invoice_number(self):
        for rec in self:
            origin = rec.env['account.invoice'].search([
                ('origin', '=', rec.origin)
            ], order='create_date asc')
            number = 1
            if origin:
                for ori in origin:
                    if rec.create_date == ori.create_date:
                        rec.invoice_installment = number
                        break
                    number += 1

    invoice_installment = fields.Integer(
        # default= lambda self:self._get_invoice_number(),
        compute="_get_invoice_number",
        string="งวดงาน"
    )

class hr_purchase_requisition_inherit(models.Model):
    _inherit = 'purchase.requisition'
    requisition_work_name = fields.Char()

class work_acceptance_inherit(models.Model):
    _inherit = 'work.acceptance'

    def _get_employee_name(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ], limit=1)
        if employee:
            return employee['name']

    date_receive_work = fields.Date(
        string="วันที่ส่งมอบงาน"
    )

    requisition_number = fields.Char(
        string="เลขที่สัญญา",
        compute="_get_requisition",
        default=False
    )

    requisition_work_name = fields.Char(
        string="ชื่องาน",
        compute="_get_requisition",
        default=False
    )

    employee_receive_name = fields.Char(
        string="ผู้จัดการใบตรวจรับงาน",
        default= lambda self: self._get_employee_name()
    )

    @api.depends("purchase_id")
    def _get_requisition(self):
        for rec in self:
            purchase_order = rec.env['purchase.order'].search([
                ('id', '=', int(rec.purchase_id[0]))
            ], limit=1)
            if purchase_order:
                rec.requisition_number = purchase_order.requisition_id.contract_number
                rec.requisition_work_name = purchase_order.requisition_id.requisition_work_name