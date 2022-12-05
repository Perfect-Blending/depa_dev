# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class BioneCustomerPayment(models.Model):

    _name = 'bione.customer.payment'
    _description = 'Customer Payment'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    # Issue17
    @api.onchange('line_ids')
    def onchange_line_ids(self):
        vat_default = 0.0
        vat_untaxed_default = 0.0
        for line in self.line_ids:
            vat_untaxed_default += line.amount_untaxed
            vat_default += line.amount_tax
        # default เมื่อกด addline
        self.amount_default_vat = vat_default
        self.amount_default_untaxed = vat_untaxed_default

        values = {}
        iml = []
        iml.append((5, 0, []))
        self.other_ids = iml
        if vat_default > 0:
            # หารหัสบัญชี ภาษีขายที่ไม่ถึงกำหนดชำระ
            params = self.env['ir.config_parameter'].sudo()
            undue_sale_tax_account_id = int(params.get_param('bione_thai_account.undue_sale_tax_account_id', default=False)) or False,
            data_other = {
                'name': undue_sale_tax_account_id,
                'amount': vat_default,
                'payment_id': False,
            }
            iml.append((0, 0, data_other))
            self.other_ids = iml

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
    @api.depends('deposit_ids')
    def _get_deposit(self):
        for receipt in self:
            receipt.amount_deposit = 0.0
            for deposit in receipt.deposit_ids:
                receipt.amount_deposit += deposit.amount_receipt

    @api.multi
    @api.depends('other_ids')
    def _get_other(self):
        for receipt in self:
            receipt.amount_other = 0.0
            for vat in receipt.other_ids:
                receipt.amount_other += vat.amount

    @api.multi
    @api.depends('banktr_ids')
    def _get_banktr(self):
        for receipt in self:
            receipt.amount_banktr = 0.0
            for vat in receipt.banktr_ids:
                receipt.amount_banktr += vat.amount

    name = fields.Char(string=u'เลขที่ใบเสร็จ', size=32, required=True, copy=False, track_visibility='onchange',
                       default='New')
    date = fields.Date(string=u'ลงวันที่', required=True, default=fields.Date.context_today, track_visibility='onchange')
    date_due = fields.Date(string=u'วันที่นัดรับเงิน', required=True, track_visibility='onchange')
    customer_id = fields.Many2one('res.partner', string=u'ลูกค้า', required=True, track_visibility='onchange')
    note = fields.Text(string=u'หมายเหตุ', track_visibility='onchange')
    line_ids = fields.One2many('bione.customer.payment.line', 'payment_id', string=u'รายการรับชำระ')
    other_ids = fields.One2many('bione.customer.payment.other', 'payment_id', string=u'อื่นๆ')
    deposit_ids = fields.One2many('bione.customer.payment.deposit', 'payment_id', string=u'มัดจำ')
    banktr_ids = fields.One2many('bione.customer.payment.bank', 'payment_id', string=u'โอน')

    amount_receipt = fields.Float(string=u'ยอดรับชำระ', compute='_get_receipts')
    change_number = fields.Boolean(string=u'เปลี่ยนเลขใบเสร็จ',)
    journal_id = fields.Many2one('account.journal', string=u'สมุดรายวันรับ', required=True)
    state = fields.Selection([('draft', 'Draft'), ('post', 'Posted'), ('cancel', 'Cancel')],
                             string=u'State', default='draft')
    amount_deposit = fields.Float(string=u'ยอดมัดจำ', track_visibility='onchange', compute='_get_deposit', copy=False)
    amount_vat = fields.Float(string=u'ยอดภาษีมูลค่าเพิ่ม', track_visibility='onchange', compute='_get_vat', copy=False)
    amount_interest = fields.Float(string=u'ดอกเบี้ยรับ', track_visibility='onchange', copy=False)
    amount_cash = fields.Float(string=u'เงินสด', track_visibility='onchange', copy=False)
    amount_cheque = fields.Float(string=u'เช็ครับ', track_visibility='onchange', compute='_get_cheque', copy=False)
    amount_wht = fields.Float(string=u'ภาษีหัก ณ ที่จ่าย', track_visibility='onchange', compute='_get_wht',
                              copy=False)
    amount_discount = fields.Float(string=u'ส่วนลดเงินสด', track_visibility='onchange', copy=False)
    amount_paid = fields.Float(string=u'ยอดรับชำระ', track_visibility='onchange', copy=False)
    amount_other = fields.Float(string=u'อื่นๆ', track_visibility='onchange', compute='_get_other', copy=False)
    amount_banktr = fields.Float(string=u'โอน', track_visibility='onchange', compute='_get_banktr', copy=False)
    cheque_ids = fields.One2many('bione.cheque', 'customer_payment_id', string=u'เช็ครับ')
    vat_ids = fields.One2many('bione.account.vat', 'customer_payment_id', string=u'ภาษีขาย')
    wht_ids = fields.One2many('bione.wht', 'customer_payment_id', string=u'ภาษีหัก ณ ที่จ่าย')
    move_id = fields.Many2one('account.move', string=u'สมุดรายวัน', index=True)
    move_line_ids = fields.One2many(related="move_id.line_ids", string="Journal Items", readonly=True, copy=False)
    amount_default_untaxed = fields.Float(string=u'Default ยอดกรวมก่อน vat', copy=False)
    amount_default_vat = fields.Float(string=u'Default ยอดภาษีมูลค่าเพิ่ม', copy=False)

    @api.onchange('date')
    def onchange_date(self):
        self.date_due = self.date

    @api.multi
    def button_post(self):
        self.ensure_one()
        #รับชำระ+ดอกเบี้ยรับ = อื่นๆ +เงินสด+ภาษีหักถูก ณ ที่จ่าย+เช็ครับ+ส่วนลดเงินสด+ยอดมัดจำ
        # if self.amount_receipt+self.amount_interest != self.amount_deposit + self.amount_cheque + self.amount_wht + self.amount_cash + self.amount_discount + self.amount_other + self.amount_banktr:
        #     raise UserError("ยอดไม่สมดุลย์")
        move = self.env['account.move']
        iml = []
        move_line = self.env['account.move.line']
        params = self.env['ir.config_parameter'].sudo()

        #Credit Side
        vat_sale_account_id = int(params.get_param('bione_thai_account.vat_sale_account_id', default=False)) or False,
        if self.amount_vat:
            move_data_vals = {
                'partner_id': self.customer_id.id,
                'invoice_id': False,
                'debit': 0.0,
                'credit': self.amount_vat,
                'payment_id': False,
                'account_id': vat_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))
        interest_income_account_id = int(params.get_param('bione_thai_account.interest_income_account_id', default=False)) or False,
        if self.amount_interest:
            move_data_vals = {
                'partner_id': self.customer_id.id,
                'invoice_id': False,
                'debit': 0.0,
                'credit': self.amount_interest,
                'payment_id': False,
                'account_id': interest_income_account_id,
            }
            iml.append((0, 0, move_data_vals))
        receivable_account_id = self.customer_id.property_account_receivable_id.id
        move_data_vals = {
            'partner_id': self.customer_id.id,
            'invoice_id': False,
            'debit': 0.0,
            'credit': self.amount_receipt - self.amount_vat,
            'payment_id': False,
            'account_id': receivable_account_id,
        }
        iml.append((0, 0, move_data_vals))

        #Debit Side

        unearned_income_account_id = int(params.get_param('bione_thai_account.unearned_income_account_id', default=False)) or False,
        if self.amount_deposit:
            move_data_vals = {
                'partner_id': self.customer_id.id,
                'invoice_id': False,
                'credit': 0.0,
                'debit': self.amount_deposit,
                'payment_id': False,
                'account_id': unearned_income_account_id,
            }
            iml.append((0,0,move_data_vals))

        cash_account_id = int(params.get_param('bione_thai_account.cash_account_id', default=False)) or False,
        if self.amount_cash:
            move_data_vals = {
                 'partner_id': self.customer_id.id,
                'invoice_id': False,
                'credit': 0.0,
                'debit': self.amount_cash,
                'payment_id': False,
                'account_id': cash_account_id,
            }
            iml.append((0, 0, move_data_vals))
        cheque_sale_account_id=int(params.get_param('bione_thai_account.cheque_sale_account_id', default=False)) or False,
        if self.amount_cheque:
            move_data_vals = {
                 'partner_id': self.customer_id.id,
                'invoice_id': False,
                'credit': 0.0,
                'debit': self.amount_cheque,
                'payment_id': False,
                'account_id': cheque_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))
        cash_discount_account_id=int(params.get_param('bione_thai_account.cash_discount_account_id', default=False)) or False,
        if self.amount_discount:
            move_data_vals = {
                 'partner_id': self.customer_id.id,
                'invoice_id': False,
                'credit': 0.0,
                'debit': self.amount_discount,
                'payment_id': False,
                'account_id': cash_discount_account_id,
            }
            iml.append((0, 0, move_data_vals))
        wht_sale_account_id=int(params.get_param('bione_thai_account.wht_sale_account_id', default=False)) or False,
        if self.amount_wht:
            move_data_vals = {
                 'partner_id': self.customer_id.id,
                'invoice_id': False,
                'credit': 0.0,
                'debit': self.amount_wht,
                'payment_id': False,
                'account_id': wht_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))
        for other in self.other_ids:
            move_data_vals = {
                 'partner_id': self.customer_id.id,
                'invoice_id': False,
                'debit': other.amount > 0 and abs(other.amount) or 0.0,
                'credit': other.amount < 0 and abs(other.amount) or 0.0,
                'payment_id': False,
                'account_id': other.name.id,
            }
            iml.append((0, 0, move_data_vals))

        for bank in self.banktr_ids:
            move_data_vals = {
                 'partner_id': self.customer_id.id,
                'invoice_id': False,
                'debit': bank.amount > 0 and abs(bank.amount) or 0.0,
                'credit': bank.amount < 0 and abs(bank.amount) or 0.0,
                'payment_id': False,
                'account_id': bank.name.id,
            }
            iml.append((0, 0, move_data_vals))


        self.state = 'post'
        move_vals = {
            'ref': self.name,
            'date': self.date,
            'company_id': self.env.user.company_id.id,
            'journal_id': self.journal_id.id,
            'partner_id': self.customer_id.id,
            'narration': self.note,
        }

        # issues 57
        # ถ้า ref ถูกใช้งานไปเเล้ว และสถานะ Unpost กับ account move ไปเเล้ว ให้เอาเลขรันสุดท้ายมาใช้ในการสร้างใบใหม่
        # และลบ Unpost นั้นทิ้ง
        domain = [('ref', '=', self.name), ('state', '=', 'draft')]
        old_move = self.env['account.move'].search(domain, limit=1)
        if old_move:
            move_vals.update({
                'name': old_move.name,
            })

        new_move = move.create(move_vals)
        new_move.sudo().write({'line_ids': iml})
        new_move.post()
        self.move_id = new_move
        # domain = [('account_id', '=', self.customer_id.property_account_receivable_id.id),
        #           ('partner_id', '=', self.customer_id.id),
        #           ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
        #           ('amount_residual_currency', '!=', 0.0)]
        # move_lines = self.env['account.move.line'].search(domain)
        # move_lines.reconcile()
        # fix Issue 287
        inv_ids = []
        for line in self.line_ids:
            inv_ids.append(line.name.id)
        to_reconcile_lines = []
        domain = [
            ('invoice_id', 'in', inv_ids),
            ('account_id', '=', self.customer_id.property_account_receivable_id.id),
            ('partner_id', '=', self.customer_id.id),
            ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
            ('amount_residual_currency', '!=', 0.0)]
        move_lines = self.env['account.move.line'].search(domain)
        domain1 = [
            ('move_id', '=', self.move_id.id),
            ('account_id', '=', self.customer_id.property_account_receivable_id.id),
            ('partner_id', '=', self.customer_id.id),
            ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
            ('amount_residual_currency', '!=', 0.0)]
        move_lines1 = self.env['account.move.line'].search(domain1)
        # print('move_lines',move_lines1)

        to_reconcile_lines.append(move_lines + move_lines1)
        # raise UserError(move_lines)
        for reconcile_lines in to_reconcile_lines:
            reconcile_lines.reconcile()

        # issues 57
        # ลบของเดิมออก
        if (old_move and self.move_id):
            old_move.unlink()
        return True

    # @api.multi
    # def button_cancel(self):
    #     self.ensure_one()
    #     self.move_id.sudo().button_cancel()
    #     self.state = 'cancel'
    #     return True

    @api.multi
    def button_cancel(self):
        self.ensure_one()
        sql = """
            select distinct full_reconcile_id from account_move_line
            where move_id = %s and full_reconcile_id is not null
        """ % (self.move_id.id)
        self._cr.execute(sql)
        full_reconcile_id = [x[0] for x in self._cr.fetchall()]
        if full_reconcile_id:
            move_sql = """
                select id from account_move_line where full_reconcile_id = %s
            """ % (full_reconcile_id[0])
            self._cr.execute(move_sql)
            move_ids = [x[0] for x in self._cr.fetchall()]
            if move_ids:
                self.env['account.move.line'].browse(move_ids).remove_move_reconcile()
        self.move_id.sudo().button_cancel()
        # self.move_id.sudo().unlink()
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
        vals['name'] = self.env['ir.sequence'].with_context(
                    ir_sequence_date=vals.get('date')).next_by_code('bione.customer.payment')
        receipt_id = super(BioneCustomerPayment, self.with_context(mail_create_nosubscribe=True)).create(vals)
        return receipt_id


class BioneCustomerPaymentDeposit(models.Model):
    _name = 'bione.customer.payment.deposit'
    _description = 'Customer Payment Deposit'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.onchange('name')
    def onchange_invoice_id(self):
        if self.name:
            self.amount_total = self.name.amount_receipt
            self.amount_residual = self.name.amount_residual

    @api.onchange('amount_receipt','amount_residual')
    # @api.depends('deposit_ids')
    def onchange_amount_receipt(self):
        if self.amount_receipt > self.amount_residual :
           raise UserError("ตัดยอดเกิน")

    name = fields.Many2one('bione.customer.deposit', string=u'ใบมัดจำ', required=True, copy=False, index=True,
                           track_visibility='onchange')
    amount_total = fields.Float(string=u'ยอดตามบิล', copy=False, track_visibility='onchange')
    amount_residual = fields.Float(string=u'ยอดค้าง', copy=False, track_visibility='onchange')
    amount_receipt = fields.Float(string=u'ยอดชำระ', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.customer.payment', string=u'รับชำระ')
    invoice_id = fields.Many2one('account.invoice', string=u'ใบแจ้งหนี้/ใบกำกับภาษี')
    # customer_id = fields.Many2one('res.partner', string=u'ลูกค้า', required=True, track_visibility='onchange')


class BioneCustomerPaymentLine(models.Model):
    _name = 'bione.customer.payment.line'
    _description = 'Customer Payment Line'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.onchange('name')
    def onchange_invoice_id(self):
        if self.name:
            self.amount_total = self.name.amount_total_signed
            self.amount_residual = self.name.residual_signed
            self.amount_receipt = self.name.residual_signed + self.name.amount_tax
            self.amount_untaxed = self.name.amount_untaxed_signed
            self.amount_tax = self.name.amount_tax

    name = fields.Many2one('account.invoice', string=u'ใบแจ้งหนี้/ใบกำกับภาษี', required=True, copy=False, index=True,
                           track_visibility='onchange')
    date_invoice = fields.Date(string=u'ลงวันที่', related='name.date_invoice', readonly=True)
    billing_id = fields.Many2one('bione.billing', string=u'เลขที่ใบวางบิล', related='name.billing_id', copy=False,
                                 index=True, track_visibility='onchange', readonly=True)
    user_id = fields.Many2one('res.users', string=u'พนักงานขาย', index=True, track_visibility='onchange')
    amount_total = fields.Float(string=u'ยอดตามบิล', copy=False, track_visibility='onchange')
    amount_residual = fields.Float(string=u'ยอดค้างชำระ', copy=False, track_visibility='onchange')
    amount_receipt = fields.Float(string=u'ยอดชำระ', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.customer.payment', string=u'รับชำระ')
    amount_untaxed = fields.Float(string=u'ยอดก่อน vat', copy=False, track_visibility='onchange')
    amount_tax = fields.Float(string=u'ยอด vat', copy=False, track_visibility='onchange')


class BioneCustomerPaymentOther(models.Model):
    _name = 'bione.customer.payment.other'
    _description = 'Customer Payment Other'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one('account.account', string=u'ผังบัญชี', required=True, copy=False, index=True,
                           track_visibility='onchange')
    amount = fields.Float(string=u'จำนวนเงิน', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.customer.payment', string=u'รับชำระ')

class BioneCustomerPaymentBank(models.Model):
    _name = 'bione.customer.payment.bank'
    _description = 'Customer Payment Bank'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one('account.account', string=u'ผังบัญชี', required=True, copy=False, index=True,
                           track_visibility='onchange')
    amount = fields.Float(string=u'จำนวนเงิน', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.customer.payment', string=u'รับชำระ')