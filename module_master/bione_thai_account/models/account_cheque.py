# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import time


class BioneCheque(models.Model):
    _name = 'bione.cheque'
    _description = 'Cheque'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'cheque_date desc,name desc'

    def _default_user_field(self):
        current_user = self._context.get('uid')
        if current_user:
            user = self.env['hr.employee'].search([('user_id', '=', current_user)], limit=1)
        else:
            user = False
        return user

    name = fields.Char(string='เลขที่เช็ค', required=True, track_visibility='onchange')

    bank_customer = fields.Char(string='ธนาคารลูกค้า', required=False, track_visibility='onchange')
    bank_branch_customer = fields.Char(string='สาขาธนาคารลูกค้า', required=False, track_visibility='onchange')

    cheque_date = fields.Date(string='ลงวันที่', required=True, track_visibility='onchange')
    cheque_date_reconcile = fields.Date(string='วันตัดธนาคาร', track_visibility='onchange')
    account_bank_id = fields.Many2one('account.journal', string='สมุดธนาคาร', requried=False, copy=False,
                                      index=True, track_visibility='onchange')
    bank = fields.Many2one('res.bank', string='ธนาคาร', related='account_bank_id.bank_id', required=False,
                           readonly=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='พาร์ทเนอร์', required=True, track_visibility='onchange')
    amount = fields.Float(string='ยอดเงิน', digits=(12,2), required=True)
    type = fields.Selection([('out', 'เช็คจ่าย'), ('in', 'เช็ครับ')], string='ประเภทเช็ค', required=True,
                            track_visibility='onchange')
    note = fields.Text(string='หมายเหตุ')
    date_cancel = fields.Datetime(string='Date Cancel', track_visibility='onchange')
    date_done = fields.Datetime(string='Date Done', track_visibility='onchange')
    date_pending = fields.Datetime(string='Date Pending', track_visibility='onchange')
    date_reject = fields.Datetime(string='Date Reject', track_visibility='onchange')
    date_assigned = fields.Datetime(string='Date Assigned', track_visibility='onchange')
    account_receipt_id = fields.Many2one('account.account', related='account_bank_id.default_debit_account_id',
                                         string='ผังบัญชีธนาคาร', required=False)
    account_pay_id = fields.Many2one('account.account', related='account_bank_id.default_credit_account_id',
                                     string='ผังบัญชีธนาคาร')
    move_line_id = fields.Many2one('account.move.line', string='Move Line', on_delete='restrict')
    move_id = fields.Many2one('account.move', string="สมุดรายวัน", on_delete='restrict')

    customer_payment_id = fields.Many2one('bione.customer.payment', string='Customer Payment', on_delete="restrict")
    customer_deposit_id = fields.Many2one('bione.customer.deposit', string='Customer Deposit', on_delete="restrict")
    customer_receipts_id = fields.Many2one('bione.customer.receipts', string='Customer Receipts', on_delete="restrict")

    supplier_payment_id = fields.Many2one('bione.supplier.payment', string='Supplier Payment', on_delete="restrict")
    supplier_deposit_id = fields.Many2one('bione.supplier.deposit', string='Supplier Deposit', on_delete="restrict")
    supplier_receipts_id = fields.Many2one('bione.supplier.receipts', string='Supplier Receipts', on_delete="restrict")

    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('assigned', 'Assigned'),
        ('pending', 'Pending'),
        ('reject', 'Reject'),
        ('done', 'Done'),
    ], string='สถานะ', default='draft', readonly=True, track_visibility='onchange')

    pay_to = fields.Many2one('res.partner', required=False, string='Pay to')
    user = fields.Many2one('hr.employee', required=False, string='Receiver', default=_default_user_field)
    strike = fields.Selection([('ACP1', '1 - ขีดคร่อมเข้าบัญชี'), ('ACP2', '2 - A/C Payee Only'), ('ACP3', '3 - &CO')], string='Strike', required=False,
                            track_visibility='onchange')

    advance_id = fields.Many2one('account.advance', string='Advance', ondeleted='cascade', index=True, )
    advance_clear_id = fields.Many2one('account.advance.clear', string='Advance Clear', ondeleted='cascade',
                                       index=True, )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pay_to = ''
        if self.partner_id:
            self.pay_to = self.partner_id

    @api.one
    def action_cancel_draft(self):
        self.state = 'draft'

    @api.one
    def action_assigned(self):
        self.state = 'assigned'
        self.date_assigned = time.strftime('%Y-%m-%d %H:%M:%S')

    @api.one
    def pending_cheque(self):
        self.state = 'pending'
        self.date_pending = time.strftime('%Y-%m-%d %H:%M:%S')

    @api.one
    def reject_cheque(self):
        self.state = 'reject'
        self.date_reject = time.strftime('%Y-%m-%d %H:%M:%S')

    @api.one
    def cancel_cheque(self):
        if self.move_id:
            self.move_id.button_cancel()
            self.move_id.unlink()
        self.state = 'cancel'
        self.date_cancel = time.strftime('%Y-%m-%d %H:%M:%S')

    @api.one
    def action_done_draft(self):
        if self.move_id:
            self.move_id.button_cancel()
            self.move_id.unlink()
        self.state = 'cancel'

    @api.one
    def action_done(self):
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        params = self.env['ir.config_parameter'].sudo()
        journal = self.env['account.journal'].search([('type', '=', 'general')])[0]
        date_reconcile = False
        iml = []
        if not self.cheque_date_reconcile:
            date_reconcile = time.strftime('%Y-%m-%d')
        else:
            date_reconcile = self.cheque_date_reconcile
        if self.type == 'out':
            gl_name = self.env['ir.sequence'].next_by_code('bione.cheque.out')
            new_voucher_no = 'QS' + self.name
            move_cheque = {
                'name': gl_name,
                'ref': self.name,
                'journal_id': journal.id,
                'narration': self.note,
                'partner_id': self.partner_id.id,
            }
            move_line_detail = {
                'name': new_voucher_no,
                'debit': 0.0,
                'credit': self.amount,
                'account_id': self.account_pay_id.id,
                'journal_id': journal.id,
                'partner_id': self.partner_id.id,
                'date': date_reconcile,
            }
            iml.append((0, 0, move_line_detail))
            cheque_purchase_account_id = int(
                params.get_param('bione_thai_account.cheque_purchase_account_id', default=False)) or False
            move_line_detail = {
                'name': self.move_line_id.account_id.name or False,
                'debit': self.amount,
                'credit': 0.0,
                'account_id': cheque_purchase_account_id, #self.move_line_id.account_id.id,
                'journal_id': journal.id,
                'partner_id': self.partner_id.id,
                'date': date_reconcile,
            }
            iml.append((0, 0, move_line_detail))
            move_id = move_pool.create(move_cheque)
            move_id.write({'name': new_voucher_no})
            move_id.sudo().write({'line_ids': iml})
            move_id.post()

            self.state = 'done'
            self.date_done = time.strftime('%Y-%m-%d %H:%M:%S')
            self.move_id = move_id.id
            self.cheque_date_reconcile = date_reconcile

        if self.type == 'in':
            gl_name = self.env['ir.sequence'].next_by_code('bione.cheque.in')
            new_voucher_no = 'QR' + self.name
            move_cheque = {
                'name': gl_name,
                'ref': self.name,
                'journal_id': journal.id,
                'narration': self.note,
                'partner_id': self.partner_id.id,
            }
            move_line_detail = {
                'name': new_voucher_no,
                'debit': self.amount,
                'credit': 0.0,
                'account_id': self.account_receipt_id.id,
                'journal_id': journal.id,
                'partner_id': self.partner_id.id,
                'date': date_reconcile,
            }
            iml.append((0, 0, move_line_detail))
            cheque_sale_account_id = int(
                params.get_param('bione_thai_account.cheque_sale_account_id', default=False)) or False,
            move_line_detail = {
                'name': self.move_line_id.account_id.name or '',
                'debit': 0.0,
                'credit': self.amount,
                'account_id': cheque_sale_account_id, #self.move_line_id.account_id.id,  # line.journal_id.default_debit_account_id.id,
                'journal_id': journal.id,
                'partner_id': self.partner_id.id,
                'date': date_reconcile,
            }
            iml.append((0, 0, move_line_detail))
            move_id = move_pool.create(move_cheque)
            move_id.write({'name': new_voucher_no})
            move_id.sudo().write({'line_ids': iml})
            move_id.post()
            self.state = 'done'
            self.date_done = time.strftime('%Y-%m-%d %H:%M:%S')
            self.move_id = move_id.id
            self.cheque_date_reconcile = date_reconcile

