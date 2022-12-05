# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import *


class AdvanceBioneSupplierReceiptsBank(models.Model):
    _inherit = 'bione.supplier.receipts.bank'
    advance_clear_id = fields.Many2one('account.advance.clear', string='Advance Clear', ondeleted='cascade', index=True)
    # type = fields.Selection(
    #     [('in', 'In')
    #      , ('out', 'Out')])


class AccountAdvanceClear(models.Model):
    _name = "account.advance.clear"
    _description = 'Advance Clear'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    _CONTROL_STATE = {"draft": [("readonly", False)]}
    _REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    _OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    STATES = [('draft', 'Draft'), ('posted', 'Posted'), ('canceled', 'Canceled')]

    @api.depends('lines', 'company_id', 'date')
    def _compute_amount(self):
        for obj in self:
            obj.amount_untaxed = sum(line.amount for line in obj.lines)
            obj.amount_total = sum(line.amount for line in obj.lines)
            obj.amount_total_signed = sum(line.amount for line in obj.lines)
            obj.amount_total_company_signed = sum(line.amount for line in obj.lines)
            obj.amount_untaxed_signed = sum(line.amount for line in obj.lines)

    # @api.depends('advance_clear_id.vat_lines')
    # @api.depends('vat_lines','wht_lines','advance_id','lines')
    # @api.multi
    @api.depends('vat_lines', 'wht_lines', 'advance_id', 'lines')
    def _compute_amount_tax(self):
        advance_clear = self.env['account.advance.clear'].search([('advance_id', '=', self.advance_id.id)])
        for obj in self.lines:
            # for include in obj.taxes:
            #     if advance_clear:
            #         self.amount_advance = round(self.advance_id.amount_total,2)
            #         for advance_amount in advance_clear:
            #             if advance_amount.state in ['posted']:
            #                 self.amount_advance -= round(advance_amount.amount_total,2)
            #     else:
            #         self.amount_advance = self.advance_id.amount_total
            #     if include.price_include==True:
            #         self.amount_untaxed = round(sum(line.amount for line in self.lines) * (100 /107),2)
            if not obj.taxes:
                if advance_clear:
                    self.amount_advance = self.advance_id.amount_total
                    for advance_amount in advance_clear:
                        if advance_amount.state in ['posted']:
                            self.amount_advance -= sum(line.amount for line in advance_amount.lines)
                    self.amount_advance += self.amount_total
                else:
                    self.amount_advance = self.advance_id.amount_total
                self.amount_untaxed = sum(line.amount for line in self.lines)

        self.amount_tax = sum(line.amount_tax for line in self.vat_lines)
        self.amount_wht = sum(line.tax for line in self.wht_lines)
        self.amount_total = round((self.amount_untaxed + self.amount_tax), 2) - round(self.amount_wht, 2)
        self.amount_diff = round(self.amount_advance, 2) - round(self.amount_total, 2)
        self.amount_total_company_signed = self.amount_total
        self.amount_untaxed_signed = self.amount_untaxed
        self.amount_total_signed = self.amount_total

        print(self.amount_total)
        print(self.amount_diff)
        print(self.amount_advance)

        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date, type="purchase", rate=self.currency_rate)
            amount_total_company_signed = currency_id.compute(self.amount_total,
                                                              self.company_id.currency_id)  # * self.currency_rate
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed,
                                                        self.company_id.currency_id)  # * self.currency_rate
            self.amount_total_company_signed = amount_total_company_signed
            self.amount_unaxed_signed = amount_untaxed_signed
            self.amount_total_signed = self.amount_total_company_signed

        # print(self.amount_total)
        if self.amount_advance > self.amount_total:
            self.write({"type": "in"})
            self.amount_balance = self.amount_diff
        else:
            self.write({"type": "out"})
            self.amount_balance = self.amount_diff * -1

        print(self.type)
        if not self.lines:
            self.amount_tax = 0.0
            self.amount_wht = 0.0
            self.amount_untaxed = 0.0
            self.amount_total = 0.0
            self.amount_diff = 0.0
            self.amount_advance = 0.0
            self.amount_total_company_signed = 0.0
            self.amount_untaxed_signed = 0.0
            self.amount_total_signed = 0.0

    @api.one
    @api.depends('lines', 'amount_total', 'amount_advance', 'date', 'currency_id', 'cheques',
                 'banktr_ids')  # ,'credit_cards','cash_moves'
    def _compute_payment_difference(self):
        if len(self.lines) == 0:
            return
        payment_difference = 0.0
        if self.lines:
            amount_to_pay = 0.0
            if self.type == 'in':
                for cq in self.cheques:
                    if cq.type == "in":
                        amount_to_pay += cq.amount
                for bm in self.banktr_ids:
                    # if bm.type=="in":
                    amount_to_pay += bm.amount
                for cm in self.cash_moves:
                    if cm.type == "in":
                        amount_to_pay += cm.amount
                # for cd in self.credit_cards:
                #     if cd.type=="in":
                #         amount_to_pay+=cd.amount
                payment_difference += self.amount_advance - (self.amount_total + amount_to_pay)
            elif self.type == 'out':
                for cq in self.cheques:
                    if cq.type == "out":
                        amount_to_pay += cq.amount
                for bm in self.banktr_ids:
                    # if bm.type=="out":
                    amount_to_pay += bm.amount
                    # amount_to_pay+=bm.fee_amount
                for cm in self.cash_moves:
                    if cm.type == "out":
                        amount_to_pay += cm.amount
                # for cd in self.credit_cards:
                #     if cd.type=="out":
                #         amount_to_pay+=cd.amount
                payment_difference += self.amount_advance - (self.amount_total - amount_to_pay)
        self.payment_difference = payment_difference

    @api.multi
    def _get_default_journal(self):
        params = self.env['ir.config_parameter'].sudo()
        return int(params.get_param('bione_thai_account.journal_id', default=False)) or False

    @api.returns('self')
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    def _get_default_account(self):
        params = self.env['ir.config_parameter'].sudo()
        return int(params.get_param('bione_thai_account.advance_account_id', default=False)) or False

    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id or self.env.user.company_id.currency_id

    @api.multi
    @api.depends('cheques', 'banktr_ids', 'payment_difference')  # 'cash_moves',,'credit_cards'
    def _paid_amount(self):
        # vals={}
        for obj in self:
            paid_cheque = 0.0
            paid_transfer = 0.0
            paid_cash = 0.0
            paid_credit_card = 0.0
            fee_amount = 0.0
            paid_diff = 0.0

            for cq in obj.cheques:
                if cq.type == "out":
                    paid_cheque -= cq.amount
            for bm in obj.banktr_ids:
                if obj.type == "in":
                    paid_transfer -= bm.amount
            #         fee_amount+=bm.fee_amount
            for cm in obj.cash_moves:
                if cm.type == "out":
                    paid_cash -= cm.amount
            if obj.payment_difference_handling == 'reconcile':
                if obj.type == 'out':
                    paid_diff = obj.payment_difference * -1
            paid_total = paid_cash + paid_cheque + paid_transfer + paid_diff
            obj.paid_cheque = paid_cheque
            obj.paid_transfer = paid_transfer
            obj.paid_cash = paid_cash
            # obj.paid_credit_card = paid_credit_card
            obj.paid_diff = paid_diff
            obj.paid_total = paid_total
            obj.fee_amount = fee_amount

    @api.multi
    @api.depends('cheques', 'banktr_ids', 'payment_difference')
    def _recv_amount(self):
        for obj in self:
            recv_cheque = 0.0
            recv_transfer = 0.0
            recv_cash = 0.0
            recv_credit_card = 0.0
            recv_total = 0.0
            recv_diff = 0.0
            for cq in obj.cheques:
                if cq.type == "in":
                    recv_cheque += cq.amount
            for bm in obj.banktr_ids:
                if obj.type == "in":
                    recv_transfer += bm.amount
            for cm in obj.cash_moves:
                if cm.type == "in":
                    recv_cash += cm.amount
            # for cd in obj.credit_cards:
            #     if cd.type=="in":
            #         recv_credit_card+=cd.amount
            if obj.payment_difference_handling == 'reconcile':
                if obj.type == 'in':
                    recv_diff = obj.payment_difference
            recv_total = recv_cash + recv_cheque + recv_transfer + recv_diff
            obj.recv_cheque = recv_cheque
            obj.recv_transfer = recv_transfer
            obj.recv_cash = recv_cash
            # obj.recv_credit_card = recv_credit_card
            obj.recv_diff = recv_diff
            obj.recv_total = recv_total
        # return vals

    # Fields
    name = fields.Char('Number', copy=False, default=lambda x: _('New'), index=True, readonly=True)
    number = fields.Char(string='Number', readonly=True, copy=False, index=True)
    date = fields.Date('Doc Date', copy=False, index=True, default=fields.Date.context_today, **_REQUIRED)
    description = fields.Char('Description', copy=False, **_OPTIONAL)
    employee_id = fields.Many2one('hr.employee', 'Employee', index=True, **_REQUIRED, default=_default_employee)
    partner_id = fields.Many2one("res.partner", string="Partner", index=True)
    notes = fields.Text(string='Notes', **_OPTIONAL)
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.user.company_id,
                                 **_REQUIRED)
    advance_id = fields.Many2one('account.advance', 'Advance', index=True, domain=[('state', '=', 'confirmed')],
                                 **_REQUIRED)
    journal_id = fields.Many2one('account.journal', 'Journal', index=True, **_REQUIRED, default=_get_default_journal)
    account_id = fields.Many2one('account.account', 'Advance Account', index=True, domain=[('deprecated', '=', False)],
                                 **_OPTIONAL, default=_get_default_account)
    # account_id = fields.Many2one('account.account', 'Advance Account',index=True,related='company_id.advance_account_id',domain=[('deprecated', '=', False)],**_OPTIONAL)
    # currency_id = fields.Many2one('res.currency', string='Currency',index=True,
    #     required=True, readonly=True, states={'draft': [('readonly', False)]},
    #     default=_default_currency, track_visibility='always')
    # currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency")
    currency_id = fields.Many2one('res.currency', string="Currency")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True, index=True)
    currency_rate = fields.Float("Exchange Rate", readonly=True, states={'draft': [('readonly', False)]},
                                 digits=(12, 6))
    currency_rate_date = fields.Date("Exchange Rate Date", readonly=True, states={'draft': [('readonly', False)]})
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount in Company Currency',
                                            currency_field='company_currency_id',
                                            store=True, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total in Currency', currency_field='currency_id',
                                          store=True, readonly=True, compute='_compute_amount',
                                          help="Total amount in the currency of the invoice.")
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency',
                                                  currency_field='company_currency_id',
                                                  store=True, readonly=True, compute='_compute_amount',
                                                  help="Total amount in the currency of the company.")
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True, index=True)
    state = fields.Selection(STATES, string='State',
                             copy=False, default='draft', track_visibility='onchange', index=True)

    lines = fields.One2many('account.advance.clear.line', 'advance_clear_id', string='Lines')
    amount_total = fields.Monetary(string='Expense Total', copy=False, store=True, compute='_compute_amount_tax')
    amount_advance = fields.Monetary(string='Advance Total', copy=False, store=True, compute='_compute_amount_tax')
    amount_diff = fields.Monetary(string='Remaining/Missing', copy=False, store=True, compute='_compute_amount_tax')
    amount_untaxed = fields.Monetary(string='Expense', store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Float(string='VAT', compute='_compute_amount_tax', track_visibility='onchange', copy=False)
    amount_wht = fields.Float(string='WHT', compute='_compute_amount_tax', track_visibility='onchange', copy=False)
    amount_balance = fields.Float(string='Balance')
    cash_moves = fields.One2many('account.cash.move', 'advance_clear_id', string='Cash', )
    cheques = fields.One2many('bione.cheque', 'advance_clear_id', string='Cheques', )
    # banktr_ids = fields.One2many('account.bank.move', 'advance_clear_id', string='Transfer',)
    banktr_ids = fields.One2many('bione.supplier.receipts.bank', 'advance_clear_id', string=u'โอน')
    # credit_cards = fields.One2many('account.credit.card', 'advance_clear_id', string='Credit Cards',)

    paid_cash = fields.Float(string='Paid Cash', store=True, readonly=True, compute='_paid_amount',
                             track_visibility='onchange')
    paid_cheque = fields.Float(string='Paid Cheque', store=True, readonly=True, compute='_paid_amount',
                               track_visibility='onchange')
    paid_transfer = fields.Float(string='Paid Transfer', store=True, readonly=True, compute='_paid_amount',
                                 track_visibility='onchange')
    # paid_credit_card = fields.Float(string='Paid Credit Card', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_diff = fields.Float(string='Paid Difference', store=True, readonly=True, compute='_paid_amount',
                             track_visibility='onchange')
    paid_total = fields.Float(string='Paid Total', store=True, readonly=True, compute='_paid_amount',
                              track_visibility='onchange')
    fee_amount = fields.Float(compute='_paid_amount', string="Fee Amount", store=True)
    recv_cheque = fields.Float(compute='_recv_amount', string="Received Cheque", store=True)
    recv_transfer = fields.Float(compute='_recv_amount', string="Received Transfer", store=True)
    recv_cash = fields.Float(compute='_recv_amount', string="Received Cash", store=True)
    # recv_credit_card = fields.Float(compute='_recv_amount',string="Received Credit Card",store=True)
    recv_diff = fields.Float(compute='_recv_amount', string="Received Difference", store=True)
    recv_total = fields.Float(compute='_recv_amount', string="Received Total", store=True)

    # vat_lines = fields.One2many('account.tax.line', 'advance_clear_id', string='VAT Lines',
    #                             readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    # wht_lines = fields.One2many('account.tax.line', 'advance_clear_id', string='WHT Lines',
    #                              readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    # vat_lines = fields.One2many('account.tax.line', 'advance_clear_id', string='VAT Lines', domain=['|',('tax_id.tax_group_id.tax_type','=','vat'),("tax_group",'=','vat')], readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    # wht_lines = fields.One2many('account.tax.line', 'advance_clear_id', string='WHT Lines', domain=[('tax_id.tax_group_id.tax_type','=','wht')], readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    vat_lines = fields.One2many('bione.account.vat', 'advance_clear_id', string=u'ภาษีซื้อ')
    wht_lines = fields.One2many('bione.wht', 'advance_clear_id', string=u'ภาษีหัก ณ ที่จ่าย')
    # manual_wht = fields.Boolean("Manual WHT :",**_REQUIRED)
    # manual_vat = fields.Boolean("Manual VAT :",**_REQUIRED)
    type = fields.Selection([
        ('in', 'in'),
        ('out', 'out')],
        copy=False, default='in', index=True)
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True, )
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')],
                                                   default='open', string
                                                   ="Payment Difference", copy=False)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, index=True)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default='Write-Off')

    @api.onchange('advance_id')
    def onchange_advance_id(self):
        self.currency_id = self.advance_id.currency_id.id
        self.currency_rate = self.advance_id.currency_rate
        self.currency_rate_date = self.advance_id.currency_rate_date

    @api.onchange('currency_id', 'date')
    def onchange_currency_id(self):
        currency_id = self.currency_id.id
        currency = self.env["res.currency"].browse(currency_id).with_context(date=self.date)
        for line in self.lines:
            line.currency_id = self.currency_id.id
        if currency:
            self.currency_rate = currency.rate
            self.currency_rate_date = currency.date

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def action_confirmed(self):
        self.state = 'confirmed'
        return True

    def _prepare_tax_line_vals(self, line, tax):
        """ Prepare values to create an account.invoice.tax line
        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = {
            'advance_clear_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            'account_id': (tax['account_id'] or line.account_id.id),
            'date': self.date
        }

        return vals

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        amount = 0.0
        taxs = 0.0
        for line in self.lines:
            for t in line.taxes:
                if t.price_include == True:
                    taxs = line.tax_amount
            taxes = line.taxes.compute_all(line.amount - taxs)['taxes']
            amount = line.amount  # round(sum(line.amount for line in self.lines),2)
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                tax_id = self.env['account.tax'].search([('id', '=', val['tax_id'])])
                for include in tax_id:
                    if include.price_include == True:
                        val['amount'] = amount - (line.amount - taxs)  # self.amount_untaxed
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    def update_compute_tax(self):
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        account_tax = self.env['account.tax.line']
        for obj in self:
            # Generate one tax line per tax, however many invoice lines it's applied to
            tax_grouped = obj.get_taxes_values()
            account_tax.search([('advance_clear_id', '=', obj.id)])
            for tax in tax_grouped.values():
                account_tax.write(tax)
            self._compute_amount_tax()

    @api.multi
    def get_advance_clear_move_lines_vat(self):
        advance_clear = self.env["account.advance.clear"].browse(self.id)
        lines = []
        # vat entries
        for vat in advance_clear.vat_lines:
            vals = {
                "account_id": vat.account_id.id,
                "debit": vat.amount,
                "credit": 0.0,
                "name": advance_clear.employee_id and _(
                    "Advance Clear for ") + advance_clear.employee_id.name or advance_clear.name,
                'ref': advance_clear.name,
                "date": vat.date,
            }
            lines.append(vals)
        return lines

    @api.multi
    def _check_func(self, fund_id, amount, _type):
        amt = 0.0
        fund_move = self.env["account.cash.move"].search([('fund_id', '=', fund_id.id)])
        for move in fund_move:
            if move.state != "posted":
                continue
            if move.type == 'in':
                amt += self.currency_id.compute(move.amount, self.company_id.currency_id)  # move.amount
            elif move.type == 'out':
                amt -= self.currency_id.compute(move.amount, self.company_id.currency_id)  # move.amount
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            # currency_rate = self.currency_rate
            if _type == 'in':
                amt += self.currency_id.compute(amount, self.company_id.currency_id)  # * currency_rate
            elif _type == 'out':
                amt -= self.currency_id.compute(amount, self.company_id.currency_id)  # * currency_rate
        else:
            if _type == 'in':
                amt += self.currency_id.compute(amount, self.company_id.currency_id)
            elif _type == 'out':
                amt -= self.currency_id.compute(amount, self.company_id.currency_id)

        return amt

    @api.multi
    def amount_partial(self):
        amount = 0.0
        for line in self.lines:
            if line.partial_type == True:
                amount += line.amount
                for include in line.taxes:
                    if include.price_include == True:
                        amount_untax = round(amount * (100 / 107), 2)
                        amount_vat = amount - amount_untax
                        amount = amount_untax + amount_vat
                    else:
                        amount += line.tax_amount
                amount = amount - line.wht_amount

        if self.amount_advance < amount:
            # amount_b = amount - self.amount_advance
            raise UserError(_('amount Advance less than the amount Advance Clearing'))

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
        for advance in self:
            currency_id = advance.currency_id.with_context(date=advance.date, type='purchase',
                                                           rate=advance.currency_rate)
            return currency_id.compute(amount, advance.company_id.currency_id)

    @api.multi
    def button_posted(self):

        # currency_rate = 1.0
        # if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
        # currency_rate = self.currency_rate
        diff_currency = self.currency_id != self.company_id.currency_id
        # self.amount_partial()
        # add fields Referent by model and id
        aref = 'account.advance.clear,%s' % (self.id)
        params = self.env['ir.config_parameter'].sudo()
        vat_account_id = int(params.get_param('bione_thai_account.vat_purchase_account_id', default=False)) or False,
        for obj in self:
            for line in obj.lines:
                if line.partial_type == True:
                    line.update({"partial_type": True})

            name_sequence = self.env['ir.sequence'].with_context(ir_sequence_date=self.date).next_by_code('account.advance.clear')

            vals = {
                "name": name_sequence,
                "ref": name_sequence,
                "origin": name_sequence,
                "aref": aref,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id': obj.company_id.id,
                'state': 'posted',
                'line_ids': [],
                'narration': obj.description,
                'partner_id': obj.employee_id.partner_id.id or 0,
            }
            # ----------------------------------------------------------
            # wht
            for wht in obj.wht_lines:
                # amount = self._convert_amount(round(wht.amount,2))
                wht_type = wht.wht_kind
                if wht_type == 'pp1':
                    wht_account_id = int(
                        params.get_param('bione_thai_account.wht_purchase1_account_id', default=False)) or False,
                elif wht_type == 'pp3':
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

                lines_vals = {
                    "account_id": wht_account_id,
                    "debit": 0.0,
                    "amount_currency": diff_currency and wht.amount,
                    "currency_id": self.currency_id.id,
                    "credit": wht.tax,
                    "name": wht.name,
                    "partner_id": wht.partner_id.id,
                    # "date": wht.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))
            for line in obj.lines:
                if line.partial_type == True:
                    # credit partial
                    amount = self._convert_amount(obj.amount_total)
                    lines_vals = {
                        "account_id": obj.account_id.id,
                        "debit": 0.0,
                        "amount_currency": diff_currency and round(obj.amount_total, 2) * -1,
                        "currency_id": obj.currency_id.id,
                        "credit": amount,
                        # "credit": round(obj.amount_total * currency_rate,2),
                        "name": obj.employee_id and _(
                        "Advance clearing payment for ") + obj.employee_id.name or obj.name,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                        "date": obj.date,
                    }
                    # vals['line_ids'].append((0, 0, lines_vals))
                else:
                    # credit
                    amount = self._convert_amount(obj.amount_advance)
                    lines_vals = {
                        "account_id": obj.account_id.id,
                        "debit": 0.0,
                        "amount_currency": diff_currency and round(obj.amount_advance, 2) * -1,
                        "currency_id": self.currency_id.id,
                        "credit": amount,
                        # "credit": round(obj.amount_advance * currency_rate,2),
                        "name": obj.employee_id and _(
                        "Advance clearing payment for ") + obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                # Make write-off entry
                if self.payment_difference and self.payment_difference_handling == 'reconcile':
                    wo_amt = round(self.payment_difference, 2)
                    debit = wo_amt > 0 and abs(wo_amt) or 0.0
                    credit = wo_amt < 0 and abs(wo_amt) or 0.0
                    amount_de = self._convert_amount(debit)
                    amount_cre = self._convert_amount(credit)
                    vals_difference = {
                        "account_id": self.writeoff_account_id.id,
                        "name": obj.employee_id and _(
                            "Advance clearing payment for ") + obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "amount_currency": diff_currency and round(wo_amt, 2),
                        "currency_id": self.currency_id.id,
                        "debit": amount_de,
                        "credit": amount_cre,
                        # "debit":round(debit * currency_rate,2),
                        # "credit": round(credit * currency_rate,2),
                    }
                    vals['line_ids'].append((0, 0, vals_difference))
            vals['line_ids'].append((0, 0, lines_vals))
            # ----------------------------------------------------------

            if self.type == 'in':
                # cash payments
                for cash in obj.cash_moves:
                    if cash.fund_id:
                        max_amount = self.env['account.petty.fund'].search([('id', '=', cash.fund_id.id)])
                        amt = self._check_func(cash.fund_id, cash.amount, cash.type)
                        if amt < 0:
                            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
                        if max_amount.max_amount < amt:
                            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
                    amount = self._convert_amount(cash.amount)
                    lines_vals = {
                        "account_id": cash.account_id.id,
                        "amount_currency": diff_currency and cash.amount,
                        "currency_id": self.currency_id.id,
                        # "debit": round(cash.amount * currency_rate,2),
                        "debit": amount,
                        "credit": 0.0,
                        "name": obj.employee_id and _(
                            "Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                    vals['line_ids'].append((0, 0, lines_vals))
                    # if cash.fund_id:
                    cash.update({"state": "posted"})
                # cash payments
                for trans in obj.banktr_ids:
                    amount = self._convert_amount(trans.amount)
                    lines_vals = {
                        "account_id": trans.name.id,
                        "amount_currency": diff_currency and trans.amount,
                        "currency_id": self.currency_id.id,
                        "debit": amount,
                        "credit": 0.0,
                        "name": obj.employee_id and _(
                            "Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "advance_clear_id": obj.id,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                    vals['line_ids'].append((0, 0, lines_vals))
                # cheque payments
                for cq in obj.cheques:
                    amount = self._convert_amount(cq.amount)
                    lines_vals = {
                        "account_id": cq.account_pay_id.id,
                        "amount_currency": diff_currency and cq.amount,
                        "currency_id": self.currency_id.id,
                        "debit": amount,
                        "credit": 0.0,
                        "name": obj.employee_id and _(
                            "Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                    vals['line_ids'].append((0, 0, lines_vals))
                    cq.update({'name': obj.name})
            else:
                # cash payments
                for cash in obj.cash_moves:
                    if cash.fund_id:
                        max_amount = self.env['account.petty.fund'].search([('id', '=', cash.fund_id.id)])
                        amt = self._check_func(cash.fund_id, cash.amount, cash.type)
                        if amt < 0:
                            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
                        if max_amount.max_amount < amt:
                            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
                    amount = self._convert_amount(cash.amount)
                    lines_vals = {
                        "account_id": cash.account_id.id,
                        "amount_currency": diff_currency and cash.amount * - 1,
                        "currency_id": self.currency_id.id,
                        "debit": 0.0,
                        # "credit":  round(cash.amount * currency_rate,2),
                        "credit": amount,
                        "name": obj.employee_id and _(
                            "Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                        # "partner_id": self.employee_id.id,
                        "date": obj.date,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                    vals['line_ids'].append((0, 0, lines_vals))
                    cash.update({"state": "posted"})
                # bank transfers
                for trans in obj.banktr_ids:
                    amount = self._convert_amount(trans.amount)
                    lines_vals = {
                        "account_id": trans.name.id,
                        "amount_currency": diff_currency,
                        "currency_id": self.currency_id.id,
                        "debit": 0.0,
                        "credit": amount,
                        "name": obj.employee_id and _(
                            "Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "advance_clear_id": obj.id,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                    vals['line_ids'].append((0, 0, lines_vals))
                # cheque payments
                for cq in obj.cheques:
                    amount = self._convert_amount(cq.amount)
                    lines_vals = {
                        "account_id": cq.account_pay_id.id,
                        "amount_currency": diff_currency and cq.amount * - 1,
                        "currency_id": self.currency_id.id,
                        "debit": 0.0,
                        "credit": amount,
                        # "credit":round(cq.amount * currency_rate,2),
                        "name": obj.employee_id and _(
                            "Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                        # "partner_id": self.employee_id.id,
                        "date": obj.date,
                        "partner_id": obj.employee_id.partner_id.id or 0,
                    }
                    vals['line_ids'].append((0, 0, lines_vals))
                    cq.update({'name': obj.name})
            # ----------------------------------------------------------
            # vat
            for vat in obj.vat_lines:
                amount = self._convert_amount(vat.amount_tax)
                lines_vals = {
                    "account_id": vat_account_id,
                    "amount_currency": diff_currency and vat.amount_tax,
                    "currency_id": self.currency_id.id,
                    "debit": amount,
                    "credit": 0.0,
                    "name": vat.name,
                    # "ref": vat.ref,
                    "partner_id": obj.employee_id.partner_id.id or 0,
                    # "partner_id": vat.partner_id.id,
                    # "date": vat.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))
                # if vat.tax_total and vat.tax_total != 0.0:
                #     lines_vals= obj.get_advance_clear_move_lines_vat(obj.id)
                #     vals['line_ids'].append((0, 0, lines_vals))

            # debit
            for line in obj.lines:
                amount = self._convert_amount(line.amount_untaxed)
                lines_vals = {
                    "account_id": line.account_id.id,
                    "amount_currency": diff_currency and round(line.amount_untaxed, 2),
                    "currency_id": self.currency_id.id,
                    "debit": amount,
                    "credit": 0.0,
                    "name": obj.employee_id and _("Advance Clearing payment for ") + obj.employee_id.name or obj.name,
                    "analytic_account_id": line.analytic_account_id.id,
                    "date": obj.date,
                    "partner_id": obj.employee_id.partner_id.id or 0,
                }
                vals['line_ids'].append((0, 0, lines_vals))

            # --------------------------------------------------------------
            # print(vals)
            move_id = self.env["account.move"].create(vals)
            self.update({"state": "posted",
                         "name":name_sequence,
                         "move_id": move_id.id,
                         })

            obj._paid_amount()
            obj._recv_amount()
            obj.update({
                "paid_cheque": obj.paid_cheque,
                "paid_transfer": obj.paid_transfer,
                "paid_cash": obj.paid_cash,
                # "paid_credit_card": obj.paid_credit_card,
                "paid_total": obj.paid_total,
                "fee_amount": obj.fee_amount,
                "recv_cheque": obj.recv_cheque,
                "recv_transfer": obj.recv_transfer,
                "recv_cash": obj.recv_cash,
                # "recv_credit_card": obj.recv_credit_card,
                "recv_total": obj.recv_total,
            })

            # print('------1--->')
            # print(obj)
            # print('------2--->')
            self._compute_amount_clear()
        return True

    @api.multi
    def get_advance_clear_move_lines_wht(self, advance_clear_id):
        advance_clear = self.env["account.advance.clear"].browse(self.id)
        lines = []
        # make entries in wht accounts
        for wht in advance_clear.wht_lines:
            vals = {
                "account_id": wht.account_id.id,
                "debit": 0.0,
                "credit": wht.amount,
                "name": advance_clear.employee_id and _(
                    "Advance Clear for ") + advance_clear.employee_id.name or advance_clear.name,
                'ref': advance_clear.name,
                "date": wht.date,
            }
            lines.append(vals)
        return lines

    def _compute_amount_clear(self):
        clearing = self.env["account.advance.clear"].search(
            [('advance_id', '=', self.advance_id.id), ('state', '<>', 'canceled')])
        amount_p = 0.0
        amount_r = 0.0
        if clearing:
            amount_total = self.advance_id.amount_total
            amount_remaining = round(sum(clear.amount_total for clear in clearing), 2)
            amount_r = self.recv_total
            amount_p = self.paid_total

            if (amount_remaining + (amount_r) - (amount_p)) >= amount_total:
                # raise UserError('done')
                self.advance_id.update({'state': 'done'})
            # raise UserError('22222')

    @api.multi
    def action_cancel(self):
        for obj in self:
            for wht in obj.wht_lines:
                # wht.action_cancel()
                wht.write({'state': 'cancel'})
            for vat in obj.vat_lines:
                vat.button_cancel()
            for cq in obj.cheques:
                cq.button_cancel()
            for bm in obj.banktr_ids:
                bm.write({'state': 'cancel'})
                # bm.action_cancel()
            for cm in obj.cash_moves:
                cm.button_cancel()

        if self.state in 'canceled':
            raise UserError(_('Not allow to cancel this document (%s)' % (self.name_get()[0][1])))
        self.write({"state": "canceled"})

        clearing = self.env["account.advance.clear"].search(
            [('advance_id', '=', self.advance_id.id), ('state', '=', 'canceled')])
        for clear in clearing:
            self.advance_id.update({"state": "confirmed"})

        return True

    @api.multi
    def button_cancel(self):
        move_obj = self.env['account.move'].browse(self.move_id.id)
        date_today = datetime.now().strftime("%Y-%m-%d")
        for obj in self:
            if obj.state == 'canceled':
                continue
            print(obj.date)
            # print(datetime.strptime(obj.date,"%Y-%m-%d"))
            cancel_date = datetime.strptime(date_today, "%Y-%m-%d")
            advance_date = obj.date  # datetime.strptime(obj.date,"%Y-%m-%d")

            if advance_date.month < cancel_date.month:
                if obj.vat_lines or obj.wht_lines:
                    raise UserError(_('You cannot cancel an advance because it is not in the current month.'))

            move = obj.move_id
            if move:
                if move.state == 'posted':
                    move_obj.reverse_moves(date_today, move.journal_id)
                else:
                    move_obj.action_reset(date_today, move.journal_id)
        self.action_cancel()
        return True

    # @api.model
    # def create(self, vals):
    #
    #     vals['name'] = self.env['ir.sequence'].with_context(
    #         ir_sequence_date=vals.get('date')).next_by_code('account.advance.clear')
    #     advance = super(AccountAdvanceClear, self).create(vals)
    #     # advance.amount_partial()
    #     return advance

    # @api.multi
    # def write(self, vals):
    #     res = super(AccountAdvanceClear, self).write(vals)
    #     return res

    @api.multi
    def unlink(self):
        check = [(obj) for obj in self if obj.state not in ('draft') or (obj.name and obj.name != '/')]
        if check:
            raise UserError(_('You cannot delete. You must cancel only.'))
        else:
            return super(AccountAdvanceClear, self).unlink()


class AccountAdvanceClearLine(models.Model):
    _name = "account.advance.clear.line"

    # Untaxed amount is used to get the amount to post in GL
    @api.depends('product_id', 'amount', 'taxes')
    def _get_amount_untaxed(self):
        tax_obj = self.env['account.tax']
        result = {}

        for line in self:
            line.amount_untaxed = line.amount
            for tax in line.taxes:
                result[line.id] = {'amount_untaxed': tax.amount, 'tax_amount': 0.0}
                if line.id:
                    line.amount_untaxed = line.amount
                    if tax.tax_group == 'vat':
                        for include in line.taxes:
                            if include.price_include == True:
                                line.amount_untaxed = line.amount * (100 / 107)
                                line.tax_amount = line.amount - line.amount_untaxed
                            else:
                                line.tax_amount = (line.amount * tax.amount) / 100
                                line.amount_untaxed = line.amount
                    if tax.tax_group == 'wht':
                        line.wht_amount = (line.amount * tax.amount) / 100
                        # line.amount_untaxed =  line.amount - line.wht_amount

    advance_clear_id = fields.Many2one('account.advance.clear', 'Advance', required=True, index=True)
    name = fields.Char('Description', required=True, index=True)
    account_id = fields.Many2one('account.account', 'Account', required=True, domain=[('deprecated', '=', False)],
                                 index=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    amount = fields.Monetary(string="Amount", required=True)
    have_receipt = fields.Boolean('Receipt', help="HAVE RECEIPT", default=True)
    partial_type = fields.Boolean('Partial', help="HAVE PARTIAL")
    # type_tax = fields.Char("type tax",compute ="_type_tax")
    # type_wht = fields.Char("type wht",compute ="_type_wht")
    # taxes = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    taxes = fields.Many2many('account.tax', 'account_advance_clear_line_tax', 'advance_clear_id', 'tax_id',
                             string='Taxes',
                             domain=[('type_tax_use', '!=', 'none'), '|', ('active', '=', False),
                                     ('active', '=', True)], oldname='invoice_line_tax_id')

    amount_untaxed = fields.Monetary(compute='_get_amount_untaxed', string="Untaxed Amount", store=True)
    tax_amount = fields.Float(compute='_get_amount_untaxed', string="Untaxed Amount", store=True)
    wht_amount = fields.Float(compute='_get_amount_untaxed', string="Untaxed Amount", store=True)
    product_id = fields.Many2one("product.product", "Product", index=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=False,
                                  related='advance_clear_id.currency_id', index=True)

    @api.onchange('product_id')
    def onchange_product(self):
        if not self.product_id:
            return {}
        prod = self.env["product.product"].browse(self.product_id.id)
        vals = {
            "name": prod.name,
            "account_id": prod.product_tmpl_id.property_account_expense_id.id or prod.categ_id.property_account_expense_categ_id.id,
            "taxes": [t.id for t in prod.supplier_taxes_id],
        }
        self.name = self.product_id.id
        return {"value": vals}

