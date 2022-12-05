# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.addons.ac_account_thai.models.num2word import num2word
from datetime import *
from odoo.tools.safe_eval import safe_eval

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'


    @api.model
    def _default_journals(self):
        voucher_type = self._context.get('voucher_type', 'sale')
        company_id = self._context.get('company_id', self.env.user.company_id)
        journal_id = False
        if company_id:
            if voucher_type == 'sale':
                journal_id = company_id.customer_cash_journal_id.id
            elif voucher_type == 'purchase':
                journal_id = company_id.vendor_cash_journal_id.id
        return self.env['account.journal'].browse(journal_id)

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        res = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
        return res

    @api.multi
    @api.depends('tax_correction', 'line_ids.price_subtotal')
    def _compute_total(self):
        for voucher in self:
            amount = 0
            vat_amount = 0
            wht_amount = 0
            for line in voucher.line_ids:
                amount += line.price_subtotal
            for vat in voucher.vat_lines:
                vat_amount += vat.amount
            if not voucher.vat_lines:
                voucher.tax_amount = 0
            for wht in voucher.wht_lines:
                wht_amount += wht.amount
            if not voucher.wht_lines:
                voucher.wht_amount = 0
            if vat_amount == 0 and wht_amount == 0:
                voucher.base = amount
                voucher.amount = amount
                voucher.tax_amount = 0
            else:
                voucher.base = amount
                voucher.amount =  amount + vat_amount -wht_amount
                voucher.tax_amount = vat_amount
                voucher.wht_amount = wht_amount
            if voucher.ref:
                voucher.tax_amount= voucher.ref.tax_amount
                voucher.wht_amount = voucher.ref.wht_amount
                voucher.amount += voucher.ref.tax_amount  -voucher.ref.wht_amount


    @api.multi
    @api.depends('cash_moves','cheques','bank_moves','credit_cards','payment_difference')
    def _paid_amount(self):
        for obj in self:
            paid_cheque=0.0
            paid_transfer=0.0
            paid_cash=0.0
            paid_credit_card =0.0
            fee_amount=0.0
            paid_diff = 0.0

            for cq in obj.cheques:
                if cq.type=="out":
                    paid_cheque+=cq.amount
            for bm in obj.bank_moves:
                if bm.type=="out":
                    paid_transfer+=bm.amount
                    fee_amount+=bm.fee_amount
            for cm in obj.cash_moves:
                if cm.type=="out":
                    paid_cash+=cm.amount
            for cd in obj.credit_cards:
                if cd.type=="out":
                    paid_credit_card+=cd.amount
            if obj.payment_difference_handling=='reconcile':
                if obj.voucher_type == 'purchase':
                    paid_diff = obj.payment_difference * -1
            paid_total=paid_cash+paid_cheque+paid_transfer+paid_credit_card+paid_diff
            obj.paid_cheque = paid_cheque
            obj.paid_transfer = paid_transfer
            obj.paid_cash = paid_cash
            obj.paid_credit_card = paid_credit_card
            obj.paid_diff = paid_diff
            obj.paid_total = paid_total
            obj.fee_amount = fee_amount

    @api.multi
    @api.depends('cash_moves','cheques','bank_moves','credit_cards','payment_difference')
    def _recv_amount(self):
        for obj in self:
            recv_cheque=0.0
            recv_transfer=0.0
            recv_cash=0.0
            recv_credit_card=0.0
            recv_total=0.0
            recv_diff = 0.0
            for cq in obj.cheques:
                if cq.type=="in":
                    recv_cheque+=cq.amount
            for bm in obj.bank_moves:
                if bm.type=="in":
                    recv_transfer+=bm.amount
            for cm in obj.cash_moves:
                if cm.type=="in":
                    recv_cash+=cm.amount
            for cd in obj.credit_cards:
                if cd.type=="in":
                    recv_credit_card+=cd.amount
            if obj.payment_difference_handling=='reconcile':
                if obj.voucher_type == 'sale':
                    recv_diff = obj.payment_difference
            recv_total=recv_cash+recv_cheque+recv_transfer+recv_credit_card+recv_diff
            obj.recv_cheque = recv_cheque
            obj.recv_transfer = recv_transfer
            obj.recv_cash = recv_cash
            obj.recv_credit_card = recv_credit_card
            obj.recv_diff = recv_diff
            obj.recv_total = recv_total
        #return vals

    @api.one
    @api.depends('line_ids', 'amount', 'date', 'currency_id','cash_moves','cheques','bank_moves','credit_cards')
    def _compute_payment_difference(self):
        if len(self.line_ids) == 0:
            return
        payment_difference = 0.0
        if self.line_ids:
            amount_to_pay =0.0
            if self.voucher_type == 'sale':
                for cq in self.cheques:
                    if cq.type=="in":
                       amount_to_pay +=cq.amount
                for bm in self.bank_moves:
                    if bm.type=="in":
                       amount_to_pay+=bm.amount
                for cm in self.cash_moves:
                    if cm.type=="in":
                       amount_to_pay+=cm.amount
                for cd in self.credit_cards:
                    if cd.type=="in":
                        amount_to_pay+=cd.amount
                payment_difference += (self.amount + amount_to_pay)
            elif self.voucher_type == 'purchase':
                for cq in self.cheques:
                    if cq.type=="out":
                        amount_to_pay+=cq.amount
                for bm in self.bank_moves:
                    if bm.type=="out":
                        amount_to_pay+=bm.amount
                        amount_to_pay+=bm.fee_amount
                for cm in self.cash_moves:
                    if cm.type=="out":
                        amount_to_pay+=cm.amount
                for cd in self.credit_cards:
                    if cd.type=="out":
                        amount_to_pay+=cd.amount
                payment_difference += (self.amount - amount_to_pay)
        self.payment_difference = payment_difference

    def get_is_refund(self):
        for obj in self:
            is_refund = False
            refund = obj.env['account.invoice'].search([('voucher_id','=',obj.id),('type','not in',('in_invoice','out_invoice'))])
            for refunds in refund:
                is_refund = True
            obj.is_refund = is_refund

    

    ref = fields.Many2one('account.voucher', string="Invoice for which this invoice is create new tax", store =True)
    currency_id = fields.Many2one('res.currency', string='Currency',required=True,default=_default_currency,readonly=True, states={'draft': [('readonly', False)]},track_visibility='always',store = True,index=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True,index=True)
    currency_rate = fields.Float("Exchange Rate", readonly=True, states={'draft': [('readonly', False)]}, digits=(12, 6))
    currency_rate_date = fields.Date("Exchange Rate Date", readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', 'Journal',
        required=True, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=_default_journals)
    pay_now = fields.Selection([
        ('pay_now', 'Pay Directly'),
        ('pay_later', 'Pay Later'),
    ], 'Payment', index=True, readonly=True, states={'draft': [('readonly', False)]}, default='pay_now')

    wht_amount = fields.Monetary(string='WHT', store=True, readonly=True, compute='_compute_total')
    vat_lines = fields.One2many('account.tax.line', 'voucher_id', string='VAT Lines', domain=['|',('tax_id.tax_group_id.tax_type','=','vat'),("tax_group",'=','vat')], readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    wht_lines = fields.One2many('account.tax.line', 'voucher_id', string='WHT Lines', domain=[('tax_id.tax_group_id.tax_type','=','wht')], readonly=True, states={'draft': [('readonly', False)]}, copy=True )
    manual_vat = fields.Boolean("Manual VAT", states={'draft': [('readonly', False)]}, copy=False)
    manual_wht = fields.Boolean("Manual WHT", states={'draft': [('readonly', False)]}, copy=False)

    cash_moves = fields.One2many('account.cash.move', 'voucher_id', string='Cash',)
    cheques = fields.One2many('account.cheque', 'voucher_id', string='Cheques',)
    bank_moves = fields.One2many('account.bank.move', 'voucher_id', string='Transfer',)
    credit_cards = fields.One2many('account.credit.card', 'voucher_id', string='Credit Cards',)
    account_id = fields.Many2one('account.account', 'Account',index=True,
       required=True, readonly=True, states={'draft': [('readonly', False)]},
       domain="[('deprecated', '=', False), ('internal_type','=', (pay_now == 'pay_now' and 'liquidity' or voucher_type == 'purchase' and 'payable' or 'receivable'))]",related='journal_id.default_debit_account_id')

    paid_cash = fields.Float(string='Paid Cash', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_cheque = fields.Float(string='Paid Cheque', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_transfer = fields.Float(string='Paid Transfer', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_credit_card = fields.Float(string='Paid Credit Card', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_diff = fields.Float(string='Paid Difference', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_total = fields.Float(string='Paid Total', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')

    fee_amount= fields.Float(compute='_paid_amount',string="Fee Amount",store=True)
    recv_cheque= fields.Float(compute='_recv_amount',string="Received Cheque",store=True)
    recv_transfer = fields.Float(compute='_recv_amount',string="Received Transfer",store=True)
    recv_cash = fields.Float(compute='_recv_amount',string="Received Cash",store=True)
    recv_credit_card = fields.Float(compute='_recv_amount',string="Received Credit Card",store=True)
    recv_diff = fields.Float(compute='_recv_amount',string="Received Difference",store=True)
    recv_total = fields.Float(compute='_recv_amount',string="Received Total",store=True)

    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True,)
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')]
        , default='open', string="Payment Difference", copy=False)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default='Write-Off')

    base = fields.Monetary(string='Total', store=True, compute='_compute_total')
    amount_word =  fields.Char(string="Amount Word", compute= '_get_amount_word')
    amount_word_eng =  fields.Char(string="Amount Word Eng", compute= '_get_amount_word')
    taxinvoice_no = fields.Char(string='Tax Invoice No.', default='', compute= '_check_doc_type')
    check_doc_type = fields.Char(string='Document Type', default='', compute= '_check_doc_type')

    cash_amount = fields.Float(string='Cash Amount', default=0, compute= '_get_cash_moves')
    bank_amount = fields.Float(string='Bank Amount', default=0, compute= '_get_bank_moves')

    check_cash = fields.Boolean("Check Cash", compute= '_check_payment_type', default=False)
    check_cheques = fields.Boolean("Check Cheques", compute= '_check_payment_type', default=False)
    check_bank = fields.Boolean("Check Bank", compute= '_check_payment_type', default=False)
    check_credit = fields.Boolean("Check Credit", compute= '_check_payment_type', default=False)

    cheque_number1 = fields.Char(string='Cheque Number 1', default='', compute= '_get_cheques')
    cheque_date1 = fields.Date(string='Cheque Date 1', default=False, compute= '_get_cheques')
    cheque_bank1 = fields.Char(string='Cheque Bank 1', default='', compute= '_get_cheques')
    cheque_branch1 = fields.Char(string='Cheque Branch 1', default='', compute= '_get_cheques')
    cheque_amount1 = fields.Float(string='Cheque Amount 1', default=0, compute= '_get_cheques')

    cheque_number2 = fields.Char(string='Cheque Number 2', default='', compute= '_get_cheques')
    cheque_date2 = fields.Date(string='Cheque Date 2', default=False, compute= '_get_cheques')
    cheque_bank2 = fields.Char(string='Cheque Bank 2', default='', compute= '_get_cheques')
    cheque_branch2 = fields.Char(string='Cheque Branch 2', default='', compute= '_get_cheques')
    cheque_amount2 = fields.Float(string='Cheque Amount 2', default=0, compute= '_get_cheques')

    credit_number1 = fields.Char(string='Credit Number 1', default='', compute= '_get_credit_cards')
    credit_date1 = fields.Date(string='Credit Date 1', default=False, compute= '_get_credit_cards')
    credit_bank1 = fields.Char(string='Credit Bank 1', default='', compute= '_get_credit_cards')
    credit_branch1 = fields.Char(string='Credit Branch 1', default='', compute= '_get_credit_cards')
    credit_amount1 = fields.Float(string='Credit Amount 1', default=0, compute= '_get_credit_cards')

    credit_number2 = fields.Char(string='Credit Number 2', default='', compute= '_get_credit_cards')
    credit_date2 = fields.Date(string='Credit Date 2', default=False, compute= '_get_credit_cards')
    credit_bank2 = fields.Char(string='Credit Bank 2', default='', compute= '_get_credit_cards')
    credit_branch2 = fields.Char(string='Credit Branch 2', default='', compute= '_get_credit_cards')
    credit_amount2 = fields.Float(string='Credit Amount 2', default=0, compute= '_get_credit_cards')

    refund_line = fields.One2many('account.invoice', 'voucher_id', string='Related Refund',readonly=True)
    is_refund = fields.Boolean("Is Refund", compute="get_is_refund", default=False)

    asset_count = fields.Integer("Count Fixed Asset", compute="get_asset_count", default=0)

    amount_signed = fields.Monetary(string='Total Signed', store=True, readonly=True, compute='_compute_total')

    @api.depends('vat_lines')
    def _check_doc_type(self):
        for obj in self:
            taxinvoice_no = ""
            doc_type = "rec"
            if obj.vat_lines:
                doc_type = "tax"
                for line in obj.vat_lines:
                    if line.tax_id.type_tax_use == 'sale' and not line.tax_id.amortized_tax_id:
                        taxinvoice_no = line.ref if taxinvoice_no == "" else taxinvoice_no

            obj.taxinvoice_no = taxinvoice_no
            obj.check_doc_type = doc_type

    @api.depends('cheques','cash_moves','bank_moves','credit_cards')
    def _check_payment_type(self):
        for obj in self:
            obj.check_cheques = (len(obj.cheques) > 0)
            obj.check_cash = (len(obj.cash_moves) > 0)
            obj.check_bank = (len(obj.bank_moves) > 0)
            obj.check_credit = (len(obj.credit_cards) > 0)

    @api.depends('cash_moves','cash_moves.amount')
    def _get_cash_moves(self):
        for obj in self:
            obj.cash_amount = 0
            for line in obj.cash_moves:
                obj.cash_amount += line.amount

    @api.depends('bank_moves','bank_moves.amount')
    def _get_bank_moves(self):
        for obj in self:
            obj.bank_amount = 0
            for line in obj.bank_moves:
                obj.bank_amount += line.amount

    @api.depends('amount')
    def _get_amount_word(self):
        for obj in self:
            if obj.amount >= 0:
                obj.amount_word = num2word(obj.amount,l='th_TH')
                obj.amount_word_eng = num2word(obj.amount,l='en_US')
            else:
                amount = obj.amount * -1
                obj.amount_word = 'ติดลบ' + num2word(amount,l='th_TH')
                obj.amount_word_eng = 'minus' + num2word(amount,l='en_US')

    @api.depends('cheques','cheques.number','cheques.date_cheque','cheques.bank_id','cheques.amount')
    def _get_cheques(self):
        for obj in self:
            obj.cheque_number1 = obj.cheque_number2 = ""
            obj.cheque_date1 = obj.cheque_date2 = False
            obj.cheque_bank1 = obj.cheque_bank2 = ""
            obj.cheque_branch1 = obj.cheque_branch2 = ""
            obj.cheque_amount1 = obj.cheque_amount2 = n = 0
            for line in obj.cheques:
                if n == 0:
                    obj.cheque_number1 = line.number
                    obj.cheque_date1 = line.date_cheque
                    obj.cheque_bank1 = line.bank_id.name
                    obj.cheque_branch1 = line.branch
                    obj.cheque_amount1 = line.amount
                elif n == 1:
                    obj.cheque_number2 = line.number
                    obj.cheque_date2 = line.date_cheque
                    obj.cheque_bank2 = line.bank_id.name
                    obj.cheque_branch2 = line.branch
                    obj.cheque_amount2 = line.amount
                n += 1

    @api.depends('credit_cards','credit_cards.number','credit_cards.date_credit_card','credit_cards.bank_id','credit_cards.amount')
    def _get_credit_cards(self):
        for obj in self:
            obj.credit_number1 = obj.credit_number2 = ""
            obj.credit_date1 = obj.credit_date2 = False
            obj.credit_bank1 = obj.credit_bank2 = ""
            obj.credit_branch1 = obj.credit_branch2 = ""
            obj.credit_amount1 = obj.credit_amount2 = n = 0
            for line in obj.credit_cards:
                if n == 0:
                    obj.credit_number1 = line.number
                    obj.credit_date1 = line.date_credit_card
                    obj.credit_bank1 = line.bank_id.name
                    obj.credit_branch1 = line.branch
                    obj.credit_amount1 = line.amount
                elif n == 1:
                    obj.credit_number2 = line.number
                    obj.credit_date2 = line.date_credit_card
                    obj.credit_bank2 = line.bank_id.name
                    obj.credit_branch2 = line.branch
                    obj.credit_amount2 = line.amount
                n += 1


    @api.onchange('currency_id','date')
    def onchange_currency_id(self):
        currency_id = self.currency_id.id
        currency = self.env["res.currency"].browse(currency_id).with_context(date=self.date)
        for line in self.line_ids:
            line.currency_id = self.currency_id.id
        if currency:
            self.currency_rate = currency.rate
            self.currency_rate_date = currency.date

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            move_obj = self.env['account.move'].browse(self.move_id.id)
            date_today = fields.Date.today()

            if voucher.state=='canceled':
                continue
            cancel_date = datetime.strptime(date_today,"%Y-%m-%d")
            advance_date = datetime.strptime(voucher.date,"%Y-%m-%d")

            if advance_date.month < cancel_date.month:
                if voucher.vat_lines or voucher.wht_lines:
                    raise UserError(_('You cannot cancel an voucher because it is not in the current month.'))

            move = voucher.move_id
            if move:
                if move.state=='posted':
                    move_obj.reverse_moves(date_today,move.journal_id)
                else:
                    move_obj.action_reset(date_today,move.journal_id)

            #voucher.move_id.button_cancel()
            #voucher.move_id.unlink()
        self.action_cancel()
        self.write({'state': 'cancel'})

    @api.multi
    def action_cancel(self):
        for obj in self:
            for wht in obj.wht_lines:
                wht.button_cancel()
            for vat in obj.vat_lines:
                vat.button_cancel()

            for cq in obj.cheques:
                cq.button_cancel()
            for cd in obj.credit_cards:
                cd.button_cancel()
            for bm in obj.bank_moves:
                bm.button_cancel()
            for cm in obj.cash_moves:
                cm.button_cancel()

        return True

    def _prepare_tax_line_vals(self, line, tax):
        """ Prepare values to create an account.invoice.tax line

        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = {
            'voucher_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            'account_id': self.voucher_type in ('sale') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id']
                 or line.account_id.id),
            }
        if not vals.get('account_analytic_id') and line.account_analytic_id and vals['account_id'] == line.account_id.id:
            vals['account_analytic_id'] = line.account_analytic_id.id

        return vals

    @api.multi
    def get_taxes_values(self):
        res = {}
        for line in self.line_ids:
            taxes = line.tax_ids.compute_all(line.price_subtotal, self.currency_id, 1, line.product_id, self.partner_id,invoice='invoice')['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                if key not in res:
                    res[key] = val
                else:
                    res[key]['amount'] += val['amount']
                    res[key]['base'] += val['base']

        return res

    @api.multi
    def compute_taxes(self):
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        account_tax_line = self.env['account.tax.line']
        ctx = dict(self._context)
        for invoice in self:
            if invoice.manual_vat:
                return
            self._cr.execute("DELETE FROM account_tax_line WHERE voucher_id=%s", (invoice.id,))
            self.invalidate_cache()

            # Generate one tax line per tax, however many invoice lines it's applied to
            tax_grouped = invoice.get_taxes_values()

            # Create new tax lines
            for tax in tax_grouped.values():
                tax.update({
                    "partner_id": invoice.partner_id and invoice.partner_id.id or False,
                    "date": invoice.date and invoice.date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })
                account_tax_line.create(tax)
            invoice._compute_total()
        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'invoice_line_ids': []})

    @api.multi
    def proforma_voucher(self):
        res = super(AccountVoucher,self).proforma_voucher()
        number = self._set_sequence()
        self.update({'number':number})
        for cq in self.cheques:
            cq.write({'name': number})
        for cc in self.credit_cards:
            cc.write({'name': number})

        return res

    @api.multi
    def _convert_amount(self, amount):
        '''
        This function convert the amount given in company currency. It takes either the rate in the voucher (if the
        payment_rate_currency_id is relevant) either the rate encoded in the system.
        :param amount: float. The amount to convert
        :param voucher: id of the voucher on which we want the conversion
        :param context: to context to use for the conversion. It may contain the key 'date' set to the voucher date
            field in order to select the good rate to use.
        :return: the amount in the currency of the voucher's company
        :rtype: float
        '''
        for voucher in self:
            currency_id = voucher.currency_id.with_context(date=voucher.date,type= voucher.voucher_type,rate = voucher.currency_rate)
            return currency_id.compute(amount, voucher.company_id.currency_id)

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        sinc = 1
        if self.voucher_type=='salf':
            sinc = 1
        elif self.voucher_type=='purchase':
            sinc = -1
        if self.paid_total == 0 and self.recv_total == 0:
            raise UserError(_("Missing Payment Method"))
        # cash payments
        for cm in self.cash_moves:
            amount = self._convert_amount(cm.amount)
            if cm.type=="in":
                debit = abs(amount) if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0
            else:
                debit = abs(amount) if amount < 0 else 0.0
                credit = abs(amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': cm.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((cm.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due,
                #'payment_id': self._context.get('payment_id'),
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
            #move_line.append(vals)
            #cm.update({"state":'posted'})
        # cheque payments
        for cq in self.cheques:
            amount = self._convert_amount(cq.amount)
            if cq.type=="in":
                debit = abs(amount) if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0
            else:
                debit = abs(amount) if amount < 0 else 0.0
                credit = abs(amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': cq.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((cq.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due,
                #'payment_id': self._context.get('payment_id'),
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
            #move_line.append(vals)
            #cq.write({'name': inv_number,"state":'posted'})

        # credit_card payments
        for cc in self.credit_cards:
            amount = self._convert_amount(cc.amount)
            if cc.type=="in":
                debit = abs(amount) if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0
            else:
                debit = abs(amount) if amount < 0 else 0.0
                credit = abs(amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit ,
                'credit': credit ,
                'account_id': cc.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((cc.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due,
                #'payment_id': self._context.get('payment_id'),
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
            #move_line.append(vals)
            #cc.write({'name': inv_number})
            #cc.write({'name': inv_number,"state":'posted'})

        # for trans in pmt.bank_moves:
        for trans in self.bank_moves:
            fee_amount = self._convert_amount((trans.fee_amount or 0.0))
            amount = self._convert_amount(trans.amount)
            if trans.type=="in":
                debit = abs(amount-fee_amount) if amount > 0 else 0.0
                credit = abs(amount-fee_amount) if amount < 0 else 0.0
            else:
                debit = abs(amount+fee_amount) if amount < 0 else 0.0
                credit = abs(amount+fee_amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit ,
                'credit': credit,
                'account_id': trans.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((trans.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due,
                'voucher_id': self.id,
                #'payment_id': self._context.get('payment_id'),
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
            #move_line.append(vals)
            if trans.fee_amount:
                #if not trans.fee_account_id:
                bank_charge_acc = self.company_id.bank_charge
                if not bank_charge_acc:
                    raise UserError(_("Missing bank charge Account"))

                # assign analytic only income,expense account with fee_amount
                #analytic_id = False
                if bank_charge_acc.user_type.report_type in ('income','expense'):
                    #analytic_id = trans.analytic_account_id and trans.analytic_account_id.id or False
                    vals = {
                        'name': self.name or '/',
                        'debit': fee_amount,
                        'credit': fee_amount,
                        'account_id': trans.account_id.id,
                        'move_id': move_id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.commercial_partner_id.id,
                        'currency_id': company_currency != current_currency and current_currency or False,
                        'amount_currency': ((fee_amount * sinc)  # amount < 0 for refunds
                            if company_currency != current_currency else 0.0),
                        'date': self.account_date,
                        'date_maturity': self.date_due,
                        'voucher_id': self.id,
                        #'payment_id': self._context.get('payment_id'),
                    }
                    self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
        ref = ''
        for wht in self.wht_lines:
            if wht.tax_id.type_tax_use=='purchase' :
                if not ref:
                    if self.voucher_type == 'purchase':
                        ref = self._set_sequence_wht()
            if not wht.amount:
                continue

            credit = 0.0
            debit  = 0.0

            if wht.tax_id.type_tax_use =="sale":
                debit = self._convert_amount(wht.amount)
            else:
                credit = self._convert_amount(wht.amount)
            vals={
                "account_id": wht.account_id.id,
                "debit": debit ,
                "credit": credit,
                "name": wht.name,
                "ref": ref,
                "partner_id": self.partner_id.id, #FIXME : should leave black
                "date": self.date,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((wht.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                "move_id":move_id,
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
            wht.update({"move_id":move_id})
        return True # move_line

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        for line in self.line_ids:
            if not line.price_subtotal:
                continue
            line_subtotal = line.price_subtotal
            if self.voucher_type == 'sale':
                line_subtotal = -1 * line.price_subtotal
            amount = self._convert_amount(line.price_subtotal)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
                'payment_id': self._context.get('payment_id'),
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)

        ref = ''
        for vat in self.vat_lines:
            amt=self.voucher_type in ["purchase"] and self._convert_amount(vat.amount) or self._convert_amount(-vat.amount)
            if vat.tax_id.type_tax_use=='sale' :
                if not ref:
                    ref = self._set_sequence_invoice()
                vat.ref = ref
            vals={
                "account_id": vat.account_id.id,
                "debit": amt>0.0 and abs(amt) or 0.0,
                "credit": amt<0.0 and abs(amt) or 0.0,
                "name": vat.name,
                "ref": ref,
                "partner_id": self.partner_id.id,
                "date": self.date,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((amt)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                "move_id":move_id,
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(vals)
            vat.update({"move_id":move_id})
        return line_total

    @api.multi
    def preview_account_move_get(self):
        move = {
            "name": '/',
            "ref": self.name,
            "journal_id": self.journal_id.id,
            "date": self.date,
            'currency_id': self.currency_id.id,
            'company_id':self.company_id.id,
            'state':'posted',
            "voucher_id": self.id,
        }
        return move

    @api.multi
    def account_move_get(self):
        if self.number:
            name = self.number
        elif self.journal_id.sequence_id:
            if not self.journal_id.sequence_id.active:
                raise UserError(_('Please activate the sequence of selected journal !'))
            name = self.journal_id.sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please define a sequence on the journal.'))

        aref = 'account.voucher,%s'%(self.id)
        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'date': self.account_date,
            'ref': self.reference,
            'aref':aref,
        }
        return move

    @api.multi
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            if not voucher.ref:
                local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
                if voucher.move_id:
                    continue
                company_currency = voucher.journal_id.company_id.currency_id.id
                current_currency = voucher.currency_id.id or company_currency
                ctx = local_context.copy()
                ctx['date'] = voucher.account_date
                ctx['check_move_validity'] = False
                if self.pay_now == 'pay_now' and self.amount > 0:
                    ctx['payment_id'] = self.env['account.payment'].create(self.voucher_pay_now_payment_create()).id
                move = self.env['account.move'].create(voucher.account_move_get())
                move_line = voucher.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency)
                move_line = self.env['account.move.line'].search([('move_id', '=', move.id)])
                total = 0
                for move_lines in move_line:
                    total += move_lines.debit - move_lines.credit
                line_total = total
                if voucher.voucher_type == 'sale':
                    line_total = line_total - voucher._convert_amount(voucher.tax_amount)
                elif voucher.voucher_type == 'purchase':
                    line_total = line_total + voucher._convert_amount(voucher.tax_amount)
                line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, move.id, company_currency, current_currency)
                voucher.write({
                    'move_id': move.id,
                    'state': 'posted',
                   # 'number': move.name
                })
                move.post()
                amount = voucher._convert_amount(voucher.amount)
                self.amount_signed = amount
            else:
                voucher.update({'state':'posted'})
        return True

    @api.multi
    def preview_first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        sinc = 1
        if self.voucher_type=='salf':
            sinc = 1
        elif self.voucher_type=='purchase':
            sinc = -1
        if self.paid_total == 0 and self.recv_total == 0:
            raise UserError(_("Missing Payment Method"))
        for cm in self.cash_moves:
            amount = self._convert_amount(cm.amount)
            if cm.type=="in":
                debit = abs(amount) if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0
            else:
                debit = abs(amount) if amount < 0 else 0.0
                credit = abs(amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': cm.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((cm.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)
        for cq in self.cheques:
            amount = self._convert_amount(cq.amount)
            if cq.type=="in":
                debit = abs(amount) if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0
            else:
                debit = abs(amount) if amount < 0 else 0.0
                credit = abs(amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': cq.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((cq.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)
        for cc in self.credit_cards:
            amount = self._convert_amount(cc.amount)
            if cc.type=="in":
                debit = abs(amount) if amount > 0 else 0.0
                credit = abs(amount) if amount < 0 else 0.0
            else:
                debit = abs(amount) if amount < 0 else 0.0
                credit = abs(amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit ,
                'credit': credit ,
                'account_id': cc.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((cc.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)

        for trans in self.bank_moves:
            fee_amount = self._convert_amount((trans.fee_amount or 0.0))
            amount = self._convert_amount(trans.amount)
            if trans.type=="in": 
                debit = abs(amount-fee_amount) if amount > 0 else 0.0
                credit = abs(amount-fee_amount) if amount < 0 else 0.0
            else:
                debit = abs(amount+fee_amount) if amount < 0 else 0.0
                credit = abs(amount+fee_amount) if amount > 0 else 0.0
            vals = {
                'name': self.name or '/',
                'debit': debit ,
                'credit': credit,
                'account_id': trans.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.commercial_partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((trans.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)
            if trans.fee_amount: 
                bank_charge_acc = self.company_id.bank_charge
                if not bank_charge_acc:
                    raise UserError(_("Missing bank charge Account"))
                if bank_charge_acc.user_type.report_type in ('income','expense'):
                    vals = {
                        'name': self.name or '/',
                        'debit': fee_amount ,
                        'credit': fee_amount,
                        'account_id': trans.account_id.id,
                        'move_id': move_id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.commercial_partner_id.id,
                        'currency_id': company_currency != current_currency and current_currency or False,
                        'amount_currency': ((fee_amount * sinc)  # amount < 0 for refunds
                            if company_currency != current_currency else 0.0),
                        'date': self.account_date,
                        'voucher_id': self.id
                    }
                    self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)
        for wht in self.wht_lines:
            credit = 0.0
            debit  = 0.0

            if wht.tax_id.type_tax_use =="sale":
                debit = self._convert_amount(wht.amount)
            else:
                credit = self._convert_amount(wht.amount)
            vals={
                "account_id": wht.account_id.id,
                "debit": debit ,
                "credit": credit ,
                "name": wht.name,
                "ref": self.number,
                "partner_id": self.partner_id.id, #FIXME : should leave black
                "date": self.date,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((wht.amount * sinc)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                "move_id":move_id,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)
        return True

    @api.multi
    def preview_voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        for line in self.line_ids:
            if not line.price_subtotal:
                continue
            line_subtotal = line.price_subtotal
            if self.voucher_type == 'sale':
                line_subtotal = -1 * line.price_subtotal
            amount = self._convert_amount(line.price_subtotal)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4,t.id) for t in line.tax_ids],
                'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(move_line)
        for vat in self.vat_lines:
            amt=self.voucher_type in ["purchase"] and self._convert_amount(vat.amount) or self._convert_amount(-vat.amount)
            vals={
                "account_id": vat.account_id.id,
                "debit": amt>0.0 and abs(amt) or 0.0,
                "credit": amt<0.0 and abs(amt) or 0.0,
                "name": vat.name,
                "ref": self.number,
                "partner_id": self.partner_id.id,
                "date": self.date,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': ((amt)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                "move_id":move_id,
                'voucher_id': self.id
            }
            self.env['account.move.preview.lines'].with_context(apply_taxes=True).create(vals)
        return line_total

    @api.multi
    def preview_action_move_line_create(self):
        for voucher in self:
            local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            move = self.env['account.move.preview'].create(voucher.preview_account_move_get())
            move_line = voucher.with_context(ctx).preview_first_move_line_get(move.id, company_currency, current_currency)
            move_line = self.env['account.move.preview.lines'].search([('move_id', '=', move.id)])
            total = 0
            for move_lines in move_line:
                total += move_lines.debit - move_lines.credit
            line_total = total
            if voucher.voucher_type == 'sale':
                line_total = line_total - voucher._convert_amount(voucher.tax_amount)
            elif voucher.voucher_type == 'purchase':
                line_total = line_total + voucher._convert_amount(voucher.tax_amount)
            line_total = voucher.with_context(ctx).preview_voucher_move_line_create(line_total, move.id, company_currency, current_currency)

            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.preview.lines'].search([('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write({'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                        'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})

        return True

    @api.multi
    def button_preview(self):
        if not self.id:
            raise UserError(_('You cannot data.'))
        else:
            move_preview = self.env['account.move.preview'].search([('voucher_id','=',self.id)])
            move_preview_line = self.env['account.move.preview.lines'].search([('voucher_id','=',self.id)])

            if not move_preview_line:
                self.preview_action_move_line_create()
            else:
                move_preview.unlink()
                move_preview_line.unlink()
                self.preview_action_move_line_create()
        return {
            'name': _('Preview Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.move.preview.lines',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':"new",
            'context':"{'action_id':active_id}",
            'domain': [('voucher_id', '=', self.id)],
        }

    @api.model
    def create(self, vals):
        voucher = super(AccountVoucher, self).create(vals)
        voucher.compute_taxes()
        return voucher

    @api.multi
    def write(self, vals):
        if 'vat_lines' in vals:
            editable=False
            if 'manual_vat' in vals:
                editable = vals['manual_vat']
            else:
                r = self.read(['manual_vat'])[0]
                editable = r['manual_vat']

        if 'wht_lines' in vals:
            editable=False
            if 'manual_wht' in vals:
                editable = vals['manual_wht']
            else:
                r = self.read(['manual_wht'])[0]
                editable = r['manual_wht']
        res = super(AccountVoucher, self).write(vals)
        if not self.line_ids:
            for vat in self.vat_lines:
                vat.unlink()
            for wht in self.wht_lines:
                wht.unlink()

        return res

    def _set_sequence(self):
        if not self:
           return
        invoice_type = self.voucher_type
        if invoice_type == "sale":
            seq =  "cash.sales"
        elif invoice_type == "purchase":
            seq = "cash.vendor"
        if not seq:
            raise UserError(_('Sequence not founded : %s'%(invoice_type)))

        sequence_id = self.env['ir.sequence'].search([('code','=',seq),('company_id','=',self.company_id.id)])
        sequence_id = sequence_id and sequence_id[0] or False
        if sequence_id:
            res = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
        return res

    def _set_sequence_wht(self):
        if not self:
           return
        seq = 'wht.purchase'
        sequence_id = self.env['ir.sequence'].search([('code','=',seq),('company_id','=',self.company_id.id)])
        sequence_id = sequence_id and sequence_id[0] or False
        if sequence_id:
            res = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Plase set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
        return res

    def _set_sequence_invoice(self):
        if not self:
           return
        seq = 'tax.invoice'
        sequence_id = self.env['ir.sequence'].search([('code','=',seq),('company_id','=',self.company_id.id)])
        sequence_id = sequence_id and sequence_id[0] or False
        if sequence_id:
            res = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
        return res

    @api.multi
    def _voucher_lines(self, lines):
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.items():
                if field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
            result.append((0, 0, values))
        return result

    @api.multi
    def get_new_tax_line(self, vou_id):
        taxs = self.env['account.tax.line'].search([('voucher_id', '=', self.id)])
        ref = ''
        if taxs:
            ref =''
            wht_ref = ''
            if self.voucher_type == 'sale':
                ref = self._set_sequence_invoice()
            if self.voucher_type == 'purchase':
                wht_ref = self._set_sequence_wht()
        for tax in taxs:
            if tax.tax_id.tax_group=='vat':
                vat_ref = ref
            if tax.tax_id.tax_group=='wht':
                vat_ref = wht_ref

            vals = {
                    'department_id': tax.department_id.id,
                    'tax_id': tax.tax_id.id,
                    'tax_group':tax.tax_group,
                    'name':tax.name,
                    'base': 0.0,
                    'amount': 0.0,
                    'ref': vat_ref,
                    'date': self.date,
                    'partner_id':tax.partner_id.id,
                    'wht_type':tax.wht_type,
                    'wht_payee':tax.wht_payee,
                    'wht_payee_other':tax.wht_payee_other,
                    'account_id':tax.account_id.id,
                    'assessable_type': tax.assessable_type,
                    'type_tax_use': tax.type_tax_use,
                    'company_id':tax.company_id.id,
                    'state': tax.state,
                    'base_total':tax.base_total,
                    'tax_total': tax.tax_total,
                    #'analytic_account_id': tax.analytic_account_id and tax.analytic_account_id.id or False,
                    'voucher_id': vou_id.id,
            }
            self.env['account.tax.line'].create(vals)
        return True

    @api.multi
    def button_get_refund(self):
        return {
            'name': _('Related Refund'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.refund_line])],
        }


    @api.multi
    def action_view_asset(self):
        xml_id = "ac_account_thai.action_account_asset_asset_form_ac_thai"
        if xml_id: 
            result = self.env.ref(xml_id).read()[0]
            asset_domain = safe_eval(result['domain'])
            asset_domain.append(('voucher_id', '=',self.id ))
            result['domain'] = asset_domain
            return result
        return True

    @api.model
    def _get_voucher_common_fields(self):
        return ['partner_id','account_id', 'currency_id', 'journal_id']

    @api.model
    def _get_refund_prepare_fields(self):
        return ['name', 'date']

    @api.model
    def _get_voucher_copy_fields(self):
        copy_fields = ['company_id']
        return self._get_voucher_common_fields() + self._get_refund_prepare_fields() + copy_fields

    @api.model
    def _prepare_voucher(self, voucher, date_voucher=None, date=None, description=None, journal_id=None, type=None):
        values = {}
        #number = self._set_sequence()
        for field in self._get_voucher_copy_fields():
            if voucher._fields[field].type == 'many2one':
                values[field] = voucher[field].id
            else:
                values[field] = voucher[field] or False

        values['line_ids'] = self._voucher_lines(voucher.line_ids)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif voucher['type'] == 'sale':
            journal = self.env['account.journal'].search([('type', '=', 'sele')], limit=1)
        values['journal_id'] = journal.id
        values['voucher_type'] = 'sale'

        values['date'] = date_voucher or fields.Date.context_today(voucher)
        values['state'] = 'draft'
        values['number'] = False
        values['partner_id'] = voucher.partner_id.id
        values['pay_now'] = voucher.pay_now


        values['state'] = 'draft'
        if date:
            values['date'] = date
        if description:
            values['name'] = description
            values['narration'] = description
        return values

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None, refund_type=None):
        #new_invoices = self.browse()
        if self.voucher_type =='sale':
            type = 'out_refund'
        else:
            type = 'in_refund'
        partner = self.partner_id
        account_id = partner.property_account_receivable_id.id
        payment_term_id = partner.property_payment_term_id.id

        invoice_vals = {
                    'origin': self.number,
                    'type': type,
                    'account_id': account_id,
                    'partner_id': partner.id,
                    'partner_shipping_id': partner.id,
                    "date_invoice" : self.date,
                    'payment_term_id': payment_term_id,
                    'company_id':self.company_id.id,
                    "date_due" : self.date,
                    "date_invoice" : self.date,
                    "date_posted" : self.account_date,
                    'currency_id': self.currency_id.id,
                    'currency_rate': self.currency_rate,
                    'currency_rate_date': self.currency_rate_date,
                    'invoice_line_ids':[],
                    'tax_line_ids': [],
                    'journal_id': self.journal_id.id,
                    'voucher_id':self.id,
        }

        for invoice in self.line_ids:
            invoice_line_vals={
                    "account_analytic_id": invoice.account_analytic_id and invoice.account_analytic_id.id or False,
                    "account_id": invoice.account_id.id,
                    #"analytic_tag_ids": self.asset_id.account_analytic_tag.id,
                    "invoice_line_tax_ids": [[6,False,invoice.tax_ids.ids]],
                    'name':invoice.name,
                    'price_unit':invoice.price_unit,
                    'quantity': invoice.quantity,
                    'price_subtotal':invoice.price_subtotal,
                    'product_id':invoice.product_id.id,
                    'uom_id': invoice.uom_id.id,
            }
            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

        refund_invoice = self.env['account.invoice'].create(invoice_vals)
        refund_invoice.compute_taxes()
        invoice_type = {
            'sale': ('customer invoices credit note'),
            'purchase': ('vendor bill credit note'),
        }

        message = _("This %s has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>") % (invoice_type[self.voucher_type], self.id,self.number)
        refund_invoice.message_post(body=message)
        return  refund_invoice

    @api.multi
    @api.returns('self')
    def create_tax(self, date_voucher=None, date=None, description=None, journal_id=None, type=None):
        new = self.browse()
        for voucher in self:

            values = self._prepare_voucher(voucher, date_voucher=date_voucher, date=date,
                                    description=description, journal_id=journal_id, type=type)

            new_voucher = self.create(values)
            voucher.get_new_tax_line(new_voucher)
            new_voucher.update({'ref':self.id,'tax_amount':self.tax_amount,'wht_amount':self.wht_amount})
            new += new_voucher
        return new

    @api.multi
    def button_get_cancel_tax(self):
        return {
            'name': _('New Sales Receipts'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.create.new.tax.voucher',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'multi': True,
            'target': 'new',
            'context':"{'action_id':active_id}",
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('menu_active',False):
            if res.get('toolbar',False):
                if res['toolbar'].get('print',False):
                    printlist = []
                    for ls in res['toolbar']['print']:
                        if ls.get('menu_active',False):
                            if self._context.get('menu_active',False) in ls.get('menu_active','').split(','):
                                printlist.append(ls)
                        else:
                            printlist.append(ls)
                    res['toolbar']['print'] = printlist
        return res



class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.depends('tax_ids')
    def _type_tax(self):
        type_tax = ""
        for obj in self:
            if obj.tax_ids:
                for tax in obj.tax_ids:
                    if tax.tax_group == 'vat' :
                        type_tax = "vat"
            obj.type_tax = type_tax
        return type_tax

    @api.depends('tax_ids')
    def _type_wht(self):
        type_wht = ""
        for obj in self:
            if obj.tax_ids:
                for tax in obj.tax_ids:
                    if tax.tax_group in ('wht'):
                        type_wht = "wht"
            obj.type_wht = type_wht
        return type_wht

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure',
        ondelete='set null', index=True, oldname='uos_id')
    quantity = fields.Float(digits=dp.get_precision('Product Price'),
        required=True, default=1)
    ref = fields.Many2one('account.voucher', related='voucher_id.ref')
    asset_id = fields.Many2one("account.asset.asset", "Asset", readonly=True,copy=False, index=True)

    type_tax = fields.Char("type tax",compute ="_type_tax")
    type_wht = fields.Char("type wht",compute ="_type_wht")

    @api.onchange('product_id','name')
    def _onchange_product_id(self):
        domain = {}
        if not self.voucher_id:
            return

        part = self.voucher_id.partner_id
        company = self.voucher_id.company_id
        currency = self.voucher_id.currency_id
        self.currency = currency.id

        if not self.product_id:
            self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref

            if product.description_purchase:
                self.name += '\n' + product.description_purchase
            if product.description_sale:
                self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if self.voucher_id.voucher_type in ('sale'):
                self.account_id = self.product_id.property_account_income_id.id
                self.tax_ids = self.product_id.taxes_id.ids
                self.price_unit = self.product_id.lst_price
            else:
                self.account_id = self.product_id.property_account_expense_id.id
                self.tax_ids = self.product_id.supplier_taxes_id.ids
                self.price_unit = self.product_id.standard_price

            if company and currency:
                currency_by_date = currency.with_context(dict(self._context or {}, date=self.voucher_id.date)).rate
                if company.currency_id != currency:
                    if company.currency_id.rate < currency_by_date:
                        self.price_unit = self.price_unit / currency_by_date
                    else:
                        self.price_unit = self.price_unit * currency_by_date

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
        return {'domain': domain}

    @api.model
    def create(self, vals):
        res = super(AccountVoucherLine, self).create(vals)
        res.voucher_id.compute_taxes()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountVoucherLine, self).write(vals)
        if 'price_unit' in vals or 'tax_ids' in vals or 'quantity' in vals or 'product_id' in vals or 'currency_id' in vals:
            self.voucher_id.compute_taxes()
        return res

    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        if self.voucher_id.voucher_type in ('sale'):
            taxes = self.product_id.taxes_id or self.account_id.tax_ids
        else:
            taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id
        taxes = taxes.filtered(lambda r: r.company_id == company_id)


