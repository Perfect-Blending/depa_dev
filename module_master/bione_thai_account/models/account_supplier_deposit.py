# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class BioneSupplierDeposit(models.Model):

    _name = 'bione.supplier.deposit'
    _description = 'Supplier Deposit'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.multi
    @api.depends('line_ids')
    def _get_receipts(self):
        for receipt in self:
            receipt.amount_receipt = 0.0
            for line in receipt.line_ids:
                receipt.amount_receipt += line.amount_receipt

    @api.multi
    @api.depends('wht_ids')
    def _get_wht(self):
        for receipt in self:
            receipt.amount_wht = 0.0
            for wht in receipt.wht_ids:
                receipt.amount_wht += wht.tax

    @api.multi
    @api.depends('cheque_ids')
    def _get_cheque(self):
        for receipt in self:
            receipt.amount_cheque = 0.0
            for cheque in receipt.cheque_ids:
                receipt.amount_cheque += cheque.amount

    @api.multi
    @api.depends('vat_ids')
    def _get_vat(self):
        for receipt in self:
            receipt.amount_vat = 0.0
            for vat in receipt.vat_ids:
                receipt.amount_vat += vat.amount_tax

    @api.multi
    @api.depends('other_ids')
    def _get_other(self):
        for receipt in self:
            receipt.amount_other = 0.0
            for vat in receipt.other_ids:
                receipt.amount_other += vat.amount

    @api.multi
    @api.depends('amount_receipt')
    def _get_payment(self):
        for receipt in self:
            receipt.amount_residual = receipt.amount_receipt
            receipt_total = 0.0
            if receipt.payment_ids:
                for payment in receipt.payment_ids:
                    if payment.invoice_id and payment.invoice_id.state not in ('cancel'):
                        receipt_total += payment.amount_receipt
                    if payment.payment_id and payment.payment_id.state not in ('cancel'):
                        receipt_total += payment.amount_receipt
            receipt.amount_residual = receipt.amount_receipt - receipt_total

    name = fields.Char(string=u'เลขที่จ่ายมัดจำ', size=32, required=True, copy=False, track_visibility='onchange',
                       default='New')
    date = fields.Date(string=u'ลงวันที่', required=True, default=fields.Date.context_today, track_visibility='onchange')
    date_due = fields.Date(string=u'วันที่นัดจ่ายเงิน', required=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string=u'ผู้จำหน่าย', required=True, track_visibility='onchange')
    note = fields.Text(string=u'หมายเหตุ', track_visibility='onchange')
    line_ids = fields.One2many('bione.supplier.deposit.line', 'payment_id', string=u'รายการจ่ายชำระ')
    other_ids = fields.One2many('bione.supplier.deposit.other', 'payment_id', string=u'อื่นๆ')
    amount_receipt = fields.Float(string=u'ยอดรับชำระ', compute='_get_receipts')
    change_number = fields.Boolean(string=u'เปลี่ยนเลขใบเสร็จ',)
    journal_id = fields.Many2one('account.journal', string=u'สมุดรายวันจ่าย', required=True)
    state = fields.Selection([('draft', 'Draft'), ('post', 'Posted'), ('cancel', 'Cancel')],
                             string=u'State', default='draft')
    amount_vat = fields.Float(string=u'ยอดภาษีมูลค่าเพิ่ม', track_visibility='onchange', compute='_get_vat', copy=False)
    amount_interest = fields.Float(string=u'ดอกเบี้ยจ่าย', track_visibility='onchange', copy=False)
    amount_cash = fields.Float(string=u'เงินสด', track_visibility='onchange', copy=False)
    amount_cheque = fields.Float(string=u'เช็คจ่าย', track_visibility='onchange', compute='_get_cheque', copy=False)
    amount_wht = fields.Float(string=u'ภาษีหัก ณ ที่จ่าย', track_visibility='onchange', compute='_get_wht',
                              copy=False)
    amount_discount = fields.Float(string=u'ส่วนลดรับ', track_visibility='onchange', copy=False)
    amount_paid = fields.Float(string=u'ยอดจ่ายชำระ', track_visibility='onchange', copy=False)
    amount_other = fields.Float(string=u'อื่นๆ', track_visibility='onchange', compute='_get_other', copy=False)
    cheque_ids = fields.One2many('bione.cheque', 'supplier_deposit_id', string=u'เช็ครับ')
    vat_ids = fields.One2many('bione.account.vat', 'supplier_deposit_id', string=u'ภาษีขาย')
    wht_ids = fields.One2many('bione.wht', 'supplier_deposit_id', string=u'ภาษีหัก ณ ที่จ่าย')

    move_id = fields.Many2one('account.move', string=u'สมุดรายวัน', index=True)
    move_line_ids = fields.One2many(related="move_id.line_ids", string="Journal Items", readonly=True, copy=False)

    amount_residual = fields.Float(string=u'ยอดคงเหลือ', compute='_get_payment', store=True)
    payment_ids = fields.One2many('bione.supplier.payment.deposit', 'name', string=u'ตัดมัดจำ')

    @api.multi
    def button_post(self):
        self.ensure_one()
        # if self.amount_receipt != self.amount_cheque + self.amount_wht + self.amount_cash + self.amount_discount + self.amount_other:
        #     raise UserError("ยอดไม่สมดุลย์")
        move = self.env['account.move']
        iml = []
        move_line = self.env['account.move.line']
        params = self.env['ir.config_parameter'].sudo()
        vat_sale_account_id = int(params.get_param('bione_thai_account.vat_purchase_account_id', default=False)) or False,
        if self.amount_vat:
            move_data_vals = {
                'partner_id': False,
                'invoice_id': False,
                'debit': self.amount_vat,
                'credit': 0.0,
                'payment_id': False,
                'account_id': vat_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))

        unearned_income_account_id = int(params.get_param('bione_thai_account.unearned_expense_account_id', default=False)) or False,
        if unearned_income_account_id:
            move_data_vals = {
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'debit': self.amount_receipt - self.amount_vat,
                'credit': 0.0,
                'payment_id': False,
                'account_id': unearned_income_account_id,
            }
            iml.append((0, 0, move_data_vals))
        cash_account_id = int(params.get_param('bione_thai_account.cash_account_id', default=False)) or False,
        if self.amount_cash:
            move_data_vals = {
                'partner_id': False,
                'invoice_id': False,
                'credit': self.amount_cash,
                'debit': 0.0,
                'payment_id': False,
                'account_id': cash_account_id,
            }
            iml.append((0, 0, move_data_vals))
        cheque_sale_account_id=int(params.get_param('bione_thai_account.cheque_purchase_account_id', default=False)) or False,
        if self.amount_cheque:
            move_data_vals = {
                'partner_id': False,
                'invoice_id': False,
                'credit': self.amount_cheque,
                'debit': 0.0,
                'payment_id': False,
                'account_id': cheque_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))
        cash_discount_account_id=int(params.get_param('bione_thai_account.cash_income_account_id', default=False)) or False,
        if self.amount_discount:
            move_data_vals = {
                'partner_id': False,
                'invoice_id': False,
                'credit': self.amount_discount,
                'debit': 0.0,
                'payment_id': False,
                'account_id': cash_discount_account_id,
            }
            iml.append((0, 0, move_data_vals))
        wht_sale_account_id=int(params.get_param('bione_thai_account.wht_purchase_account_id', default=False)) or False,
        if self.amount_wht:
            move_data_vals = {
                'partner_id': False,
                'invoice_id': False,
                'credit':self.amount_wht,
                'debit': 0.0,
                'payment_id': False,
                'account_id': wht_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))
        for other in self.other_ids:
            move_data_vals = {
                'partner_id': False,
                'invoice_id': False,
                'debit': other.amount < 0 and abs(other.amount) or 0.0,
                'credit': other.amount > 0 and abs(other.amount) or 0.0,
                'payment_id': False,
                'account_id': other.name.id,
            }
            iml.append((0, 0, move_data_vals))
        self.state = 'post'
        move_vals = {
            'ref': self.name,
            'date': self.date,
            'company_id': self.env.user.company_id.id,
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'narration': self.note,
        }
        new_move = move.create(move_vals)
        new_move.sudo().write({'line_ids': iml})
        new_move.post()
        self.move_id = new_move
        return True

    @api.multi
    def button_cancel(self):
        self.ensure_one()
        self.move_id.sudo().button_cancel()
        self.state = 'cancel'
        return True

    @api.multi
    def button_draft(self):
        self.ensure_one()
        self.move_id = False
        self.state = 'draft'
        return True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bione.supplier.deposit')
        receipt_id = super(BioneSupplierDeposit, self.with_context(mail_create_nosubscribe=True)).create(vals)
        return receipt_id


class BioneSupplierDepositLine(models.Model):
    _name = 'bione.supplier.deposit.line'
    _description = 'Supplier Deposit Line'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string=u'คำอธิบาย', required=True, index=True, copy=False, track_visibility='onchange')
    amount_receipt = fields.Float(string=u'ยอดชำระ', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.supplier.deposit', string=u'รับมัดจำ')


class BioneSupplierDepositOther(models.Model):
    _name = 'bione.supplier.deposit.other'
    _description = 'Supplier Deposit Other'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one('account.account', string=u'ผังบัญชี', required=True, copy=False, index=True,
                           track_visibility='onchange')
    amount = fields.Float(string=u'จำนวนเงิน', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.supplier.deposit', string=u'รับมัดจำ')

