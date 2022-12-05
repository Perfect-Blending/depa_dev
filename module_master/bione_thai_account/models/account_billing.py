# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BioneBilling(models.Model):

    @api.multi
    @api.depends('name','date','date_due','customer_id')
    def _get_amount(self):
        out_invoice = 0.00
        out_refund = 0.00
        for invoice in self.invoice_ids:
            out_invoice += invoice.residual
        for invoice in self.refund_ids:
            out_refund -= invoice.residual
        self.amount_residual = out_invoice
        self.amount_refund = out_refund
        self.amount_billing = out_invoice + out_refund

    _name = 'bione.billing'
    _description = 'Billing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='เลขที่ใบวางบิล', size=32, required=True, copy=False, track_visibility='onchange',
                       default=lambda self: self.env['ir.sequence'].next_by_code('bione.billing'))
    date = fields.Date(string='ลงวันที่', required=True, default=fields.Date.context_today, track_visibility='onchange')
    date_due = fields.Date(string='กำหนดชำระ', required=True, track_visibility='onchange')
    customer_id = fields.Many2one('res.partner', string='ลูกค้า', required=True, track_visibility='onchange')
    note = fields.Text(string='หมายเหตุ', track_visibility='onchange')
    invoice_ids = fields.Many2many('account.invoice', 'billing_invoice_rel', 'billing_id', 'invoice_id',
                                    string='ใบแจ้งหนี้/ใบกำกับภาษี')
    refund_ids = fields.Many2many('account.invoice', 'billing_invoice_refund_rel', 'billing_id', 'invoice_id',
                                   string='ใบลดหนี้')
    amount_residual = fields.Float(compute='_get_amount', string='ยอดหนี้คงค้าง', digits=(12, 2),store=True)
    amount_refund = fields.Float(compute='_get_amount', string='ยอดลดหนี้', digits=(12, 2) ,store=True)
    amount_billing = fields.Float(compute='_get_amount', string='รวมเป็นเงิน', digits=(12, 2), store=True)
    change_number = fields.Boolean(string='เปลี่ยนเลขใบวางบิล',)

    _sql_constraints = [
        ('name', 'unique( name )', 'เลขที่วางบิลห้ามซ้ำ.')
    ]

    @api.multi
    def updateInvoice(self):
        # print ('Do Update Billing')
        for billing in self:
            for invoice in billing.invoice_ids:
                #print(invoice.id)
                update_sql = """  
                    update account_invoice
                    set billing_id = %s
                    where id = %s and type = 'out_invoice'
                """ % (billing.id, invoice.id)
                self._cr.execute(update_sql)
            for refund in billing.refund_ids:
                update_sql = """  
                    update account_invoice
                    set billing_id = %s
                    where id = %s and type = 'out_refund'
                """ % (billing.id, refund.id)
                self._cr.execute(update_sql)

    @api.multi
    def clearInvoice(self):
        for billing in self:
            sql = """
                update account_invoice
                set billing_id = null
                where billing_id = %s
            """ % (billing.id)
            self._cr.execute(sql)

    @api.multi
    def write(self, vals):
        self.clearInvoice()
        res = super(BioneBilling, self).write(vals)
        self.updateInvoice()
        return res

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bione.billing')
        bill_id = super(BioneBilling, self.with_context(mail_create_nosubscribe=True)).create(vals)
        bill_id.updateInvoice()
        return bill_id

