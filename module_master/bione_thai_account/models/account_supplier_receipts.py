# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class BioneSupplierReceipts(models.Model):

    _name = 'bione.supplier.receipts'
    _description = 'Supplier Receipts'
    _order = 'name'
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
    @api.depends('banktr_ids')
    def _get_banktr(self):
        for receipt in self:
            receipt.amount_banktr = 0.0
            for vat in receipt.banktr_ids:
                receipt.amount_banktr += vat.amount

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

    name = fields.Char(string=u'เลขที่ซื้อสด', size=32, required=True, copy=False, track_visibility='onchange',
                       default='New')
    date = fields.Date(string=u'ลงวันที่', required=True, default=fields.Date.context_today, track_visibility='onchange')
    date_due = fields.Date(string=u'วันที่นัดจ่ายเงิน', required=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string=u'ผู้จำหน่าย', required=True, track_visibility='onchange')
    note = fields.Text(string=u'หมายเหตุ', track_visibility='onchange')
    line_ids = fields.One2many('bione.supplier.receipts.line', 'payment_id', string=u'รายการจ่ายชำระ')
    other_ids = fields.One2many('bione.supplier.receipts.other', 'payment_id', string=u'อื่นๆ')
    banktr_ids = fields.One2many('bione.supplier.receipts.bank', 'payment_id', string=u'โอน')

    amount_receipt = fields.Float(string=u'ยอดรับชำระ', compute='_get_receipts')
    change_number = fields.Boolean(string=u'เปลี่ยนเลขใบซื้อสด',)
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
    amount_banktr = fields.Float(string=u'โอน', track_visibility='onchange', compute='_get_banktr', copy=False)

    cheque_ids = fields.One2many('bione.cheque', 'supplier_receipts_id', string=u'เช็คจ่าย')
    vat_ids = fields.One2many('bione.account.vat', 'supplier_receipts_id', string=u'ภาษีซื้อ')
    wht_ids = fields.One2many('bione.wht', 'supplier_receipts_id', string=u'ภาษีหัก ณ ที่จ่าย')

    move_id = fields.Many2one('account.move', string=u'สมุดรายวัน', index=True)
    move_line_ids = fields.One2many(related="move_id.line_ids", string="Journal Items", readonly=True, copy=False)

    amount_residual = fields.Float(string=u'ยอดคงเหลือ', compute='_get_payment', store=True)
    payment_ids = fields.One2many('bione.supplier.payment.deposit', 'name', string=u'ตัดมัดจำ')

    @api.onchange('partner_id', 'date')
    def _onchange_partner_id_date(self):
        date_invoice = self.date
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if self.partner_id.property_supplier_payment_term_id.id:
            pterm = self.partner_id.property_supplier_payment_term_id
            pterm_list = pterm.compute(value=1, date_ref=date_invoice)[0]
            self.date_due = max(line[0] for line in pterm_list)
        if self.date_due and (date_invoice > self.date_due):
            self.date_due = date_invoice

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
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'debit': self.amount_vat,
                'credit': 0.0,
                'payment_id': False,
                'account_id': vat_sale_account_id,
            }
            iml.append((0, 0, move_data_vals))

        # unearned_income_account_id = int(params.get_param('bione_thai_account.unearned_expense_account_id', default=False)) or False,
        # if unearned_income_account_id:
        #     move_data_vals = {
        #         'partner_id': self.partner_id.id,
        #         'invoice_id': False,
        #         'debit': self.amount_receipt - self.amount_vat,
        #         'credit': 0.0,
        #         'payment_id': False,
        #         'account_id': unearned_income_account_id,
        #     }
        #     iml.append((0, 0, move_data_vals))

        for line in self.line_ids:
            move_data_vals = {
                'name':line.name,
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'debit': line.amount_receipt > 0 and abs(line.amount_receipt) or 0.0,
                'credit': line.amount_receipt < 0 and abs(line.amount_receipt) or 0.0,
                'payment_id': False,
                'account_id': line.account_id.id,
                'analytic_account_id': line.account_analytic_id.id,
                'cost_center_id': line.cost_center_id.id,
            }
            iml.append((0, 0, move_data_vals))

        cash_account_id = int(params.get_param('bione_thai_account.cash_account_id', default=False)) or False,
        if self.amount_cash:
            move_data_vals = {
                'partner_id': self.partner_id.id,
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
                'partner_id': self.partner_id.id,
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
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'credit': self.amount_discount,
                'debit': 0.0,
                'payment_id': False,
                'account_id': cash_discount_account_id,
            }
            iml.append((0, 0, move_data_vals))
        # wht_sale_account_id=int(params.get_param('bione_thai_account.wht_purchase_account_id', default=False)) or False,
        # if self.amount_wht:
        #     move_data_vals = {
        #         'partner_id': self.partner_id.id,
        #         'invoice_id': False,
        #         'credit':self.amount_wht,
        #         'debit': 0.0,
        #         'payment_id': False,
        #         'account_id': wht_sale_account_id,
        #     }
        #     iml.append((0, 0, move_data_vals))

        # ----------------------------------------------------------
        # wht
        for wht in self.wht_ids:
            wht_type = wht.wht_kind
            if wht_type == 'pp1':
                wht_account_id = int(
                    params.get_param('bione_thai_account.wht_purchase1_account_id', default=False)) or False,
            elif wht_type == 'pp2':
                wht_account_id = int(
                    params.get_param('bione_thai_account.wht_purchase2_account_id', default=False)) or False,
            elif wht_type == 'pp4':
                wht_account_id = int(
                    params.get_param('bione_thai_account.wht_purchase3_account_id', default=False)) or False,
            elif wht_type == 'pp7':
                wht_account_id = int(
                    params.get_param('bione_thai_account.wht_purchase53_account_id', default=False)) or False,
            else:
                wht_account_id = int(
                    params.get_param('bione_thai_account.wht_purchase_account_id', default=False)) or False,

            move_data_vals = {
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'credit': wht.tax,
                'debit': 0.0,
                'payment_id': False,
                'account_id': wht_account_id,
            }
            iml.append((0, 0, move_data_vals))

        for other in self.other_ids:
            move_data_vals = {
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'debit': other.amount < 0 and abs(other.amount) or 0.0,
                'credit': other.amount > 0 and abs(other.amount) or 0.0,
                'payment_id': False,
                'account_id': other.name.id,
            }
            iml.append((0, 0, move_data_vals))

        for bank in self.banktr_ids:
            move_data_vals = {
                'partner_id': self.partner_id.id,
                'invoice_id': False,
                'debit': bank.amount < 0 and abs(bank.amount) or 0.0,
                'credit': bank.amount > 0 and abs(bank.amount) or 0.0,
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
            'partner_id': self.partner_id.id,
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

        # issues 57
        # ลบของเดิมออก
        if(old_move and self.move_id):
            old_move.unlink()

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
        vals['name'] = self.env['ir.sequence'].with_context(
            ir_sequence_date=vals.get('date')).next_by_code('bione.supplier.receipts')
        receipt_id = super(BioneSupplierReceipts, self.with_context(mail_create_nosubscribe=True)).create(vals)
        return receipt_id


class BioneSupplierReceiptsLine(models.Model):
    _name = 'bione.supplier.receipts.line'
    _description = 'Supplier Receipts Line'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string=u'คำอธิบาย', required=True, index=True, copy=False, track_visibility='onchange')
    # amount_receipt = fields.Float(string=u'ยอดชำระ', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.supplier.receipts', string=u'ซื้อสด')

    sequence = fields.Integer(default=10,
                              help="Gives the sequence of this line when displaying the voucher.")
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='set null', index=True)
    account_id = fields.Many2one('account.account', string='Account',
                                 required=True, domain=[('deprecated', '=', False)],
                                 help="The income or expense account related to the selected product.")
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'),
                              oldname='amount')
    amount_receipt = fields.Float(string='Amount',
                                     store=True, readonly=True, compute='_compute_subtotal')
    quantity = fields.Float(digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)

    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    cost_center_id = fields.Many2one('account.cost.center', 'Cost Center')
    # analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    # tax_ids = fields.Many2many('account.tax', string='Tax', help="Only for tax excluded from price")



    @api.one
    @api.depends('price_unit', 'quantity', 'product_id')
    def _compute_subtotal(self):
        self.amount_receipt = self.quantity * self.price_unit
        # if self.tax_ids:
        #     taxes = self.tax_ids.compute_all(self.price_unit, self.quantity, product=self.product_id)
        #     self.amount_receipt = taxes['total_excluded']


    @api.onchange('product_id', 'payment_id')
    def _onchange_line_details(self):
        if not self.payment_id or not self.product_id or not self.payment_id.partner_id:
            return
        onchange_res = self.product_id_change(
            self.product_id.id,
            self.payment_id.partner_id.id,
            self.price_unit)
        for fname, fvalue in onchange_res['value'].items():
            setattr(self, fname, fvalue)

    def _get_account(self, product, fpos, type):
        accounts = product.product_tmpl_id.get_product_accounts(fpos)
        if type == 'sale':
            return accounts['income']
        return accounts['expense']

    @api.multi
    def product_id_change(self, product_id, partner_id=False, price_unit=False):
        # TDE note: mix of old and new onchange badly written in 9, multi but does not use record set
        context = self._context
        # company_id = company_id if company_id is not None else context.get('company_id', False)
        # company = self.env['res.company'].browse(company_id)
        # currency = self.env['res.currency'].browse(currency_id)
        if not partner_id:
            raise UserError(_("You must first select a partner."))
        part = self.env['res.partner'].browse(partner_id)
        if part.lang:
            self = self.with_context(lang=part.lang)

        product = self.env['product.product'].browse(product_id)
        fpos = part.property_account_position_id
        account = self._get_account(product, fpos, type)
        values = {
            'name': product.partner_ref,
            'account_id': account.id,
        }

        # if type == 'purchase':
        #     values['price_unit'] = price_unit or product.standard_price
        #     taxes = product.supplier_taxes_id or account.tax_ids
        #     if product.description_purchase:
        #         values['name'] += '\n' + product.description_purchase
        # else:
        #     values['price_unit'] = price_unit or product.lst_price
        #     taxes = product.taxes_id or account.tax_ids
        #     if product.description_sale:
        #         values['name'] += '\n' + product.description_sale
        #
        # values['tax_ids'] = taxes.ids

        # if company and currency:
        #     if company.currency_id != currency:
        #         if type == 'purchase':
        #             values['price_unit'] = price_unit or product.standard_price
        #         values['price_unit'] = values['price_unit'] * currency.rate

        return {'value': values, 'domain': {}}










class BioneSupplierReceiptsOther(models.Model):
    _name = 'bione.supplier.receipts.other'
    _description = 'Supplier Receipts Other'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one('account.account', string=u'ผังบัญชี', required=True, copy=False, index=True,
                           track_visibility='onchange')
    amount = fields.Float(string=u'จำนวนเงิน', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.supplier.receipts', string=u'ซื้อสด')

class BioneSupplierReceiptsBank(models.Model):
    _name = 'bione.supplier.receipts.bank'
    _description = 'Supplier Receipts Bank'

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one('account.account', string=u'ผังบัญชี', required=True, copy=False, index=True,
                           track_visibility='onchange')
    amount = fields.Float(string=u'จำนวนเงิน', copy=False, track_visibility='onchange')
    payment_id = fields.Many2one('bione.supplier.receipts', string=u'ซื้อสด')
