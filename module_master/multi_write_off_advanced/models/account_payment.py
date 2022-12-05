# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError

class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"
    
    payment_option = fields.Selection([('full','Full Payment without Deduction'),('partial','Full Payment with Deduction')], default='full', required=True, string='Payment Option')
    amount_pay_total = fields.Float('Amount Total', readonly=1)
    writeoff_multi_acc_ids = fields.One2many('writeoff.multi', 'register_id', string='Write Off Accounts')
    
    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)
        rec.update({
            'amount_pay_total': rec['amount'],
        })
        return rec
    
    @api.onchange('writeoff_multi_acc_ids')
    @api.multi
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount_payment for line in self.writeoff_multi_acc_ids])
            self.amount = self.amount_pay_total - diff_amount
            
    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(account_register_payments, self)._prepare_payment_vals(invoices)
        if self.writeoff_multi_acc_ids:
            multi_accounts = []
            diff_amount = 0.0
            for line in self.writeoff_multi_acc_ids:
                multi_accounts.append((0,0,{'writeoff_account_id': line.writeoff_account_id.id,
                                            'name': line.name or '',
                                            'amt_percent': line.amt_percent or '',
                                            'amount': line.amount_payment or '',
                                            'currency_id': line.currency_id and line.currency_id.id or ''}))
                diff_amount += line.amount_payment
            res.update({
                'payment_option': 'partial',
                'payment_difference_handling': 'reconcile',
                'post_diff_acc': 'multi',
                'payment_difference': diff_amount,
                'writeoff_multi_acc_ids': multi_accounts
                })
        return res
    
    
class account_payment(models.Model):
    _inherit = "account.payment"
    
    payment_option = fields.Selection([('full','Full Payment without Deduction'),('partial','Full Payment with Deduction')], default='full', required=True, string='Payment Option')
    post_diff_acc = fields.Selection([('single','Single Account'),('multi','Multiple Accounts')], default='single', string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_id', string='Write Off Accounts')
    
    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'full':
            self.payment_difference_handling = 'open'
            self.post_diff_acc = 'single'
        else:
            self.payment_difference_handling = 'reconcile'
            self.post_diff_acc = 'multi'
            
    @api.onchange('writeoff_multi_acc_ids')
    @api.multi
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.writeoff_multi_acc_ids])
            self.amount = self.invoice_ids and self.invoice_ids[0].residual - diff_amount
    
    @api.multi
    def post(self):
        if self.payment_difference_handling == 'reconcile' and self.post_diff_acc == 'multi':
            amount = 0
            for payment in self.writeoff_multi_acc_ids:
                amount += payment.amount
            if self.payment_type == 'inbound' and round(self.payment_difference,2) != round(amount,2):
                raise UserError(_("The sum of write off amounts and payment difference amounts are not equal."))
            elif self.payment_type == 'outbound' and round(self.payment_difference,2) != -round(amount,2):
                raise UserError(_("The sum of write off amounts and payment difference amounts are not equal."))
        return  super(account_payment, self).post()
    
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        
        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            if self.post_diff_acc == 'single':
                writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)[2:]
                # the writeoff debit and credit must be computed from the invoice residual in company currency
                # minus the payment amount in company currency, and not from the payment difference in the payment currency
                # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
                total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
                total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
                if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                    amount_wo = total_payment_company_signed - total_residual_company_signed
                else:
                    amount_wo = total_residual_company_signed - total_payment_company_signed
                # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
                # amount in the company currency
                if amount_wo > 0:
                    debit_wo = amount_wo
                    credit_wo = 0.0
                    amount_currency_wo = abs(amount_currency_wo)
                else:
                    debit_wo = 0.0
                    credit_wo = -amount_wo
                    amount_currency_wo = -abs(amount_currency_wo)
                writeoff_line['name'] = self.writeoff_label
                writeoff_line['account_id'] = self.writeoff_account_id.id
                writeoff_line['debit'] = debit_wo
                writeoff_line['credit'] = credit_wo
                writeoff_line['amount_currency'] = amount_currency_wo
                writeoff_line['currency_id'] = currency_id
                writeoff_line = aml_obj.create(writeoff_line)
                if counterpart_aml['debit'] or writeoff_line['credit']:
                    counterpart_aml['debit'] += credit_wo - debit_wo
                if counterpart_aml['credit'] or writeoff_line['debit']:
                    counterpart_aml['credit'] += debit_wo - credit_wo
                counterpart_aml['amount_currency'] -= amount_currency_wo
            
            if self.post_diff_acc == 'multi':
                for woff_payment in self.writeoff_multi_acc_ids:
                    writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                    amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(woff_payment.amount, self.currency_id, self.company_id.currency_id)[2:]
                    
                    if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                        amount_wo = - woff_payment.amount
                    else:
                        amount_wo = woff_payment.amount
                    # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
                    # amount in the company currency
                
                    if amount_wo > 0:
                        debit_wo = amount_wo
                        credit_wo = 0.0
                        amount_currency_wo = abs(amount_currency_wo)
                    else:
                        debit_wo = 0.0
                        credit_wo = -amount_wo
                        amount_currency_wo = -abs(amount_currency_wo)
                    
                    writeoff_line['name'] = woff_payment.name
                    writeoff_line['account_id'] = woff_payment.writeoff_account_id.id
                    writeoff_line['debit'] = debit_wo
                    writeoff_line['credit'] = credit_wo
                    writeoff_line['amount_currency'] = amount_currency_wo
                    writeoff_line['currency_id'] = currency_id
                    writeoff_line = aml_obj.create(writeoff_line)
                    if counterpart_aml['debit'] or writeoff_line['credit']:
                        counterpart_aml['debit'] += credit_wo - debit_wo
                    if counterpart_aml['credit'] or writeoff_line['debit']:
                        counterpart_aml['credit'] += debit_wo - credit_wo
                    counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        self.invoice_ids.register_payment(counterpart_aml)

        return move
    
class writeoff_accounts(models.Model):
    _name = 'writeoff.accounts'
    
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    amt_percent = fields.Float(string='Amount(%)', digits=(16,2))
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_id = fields.Many2one('account.payment', string='Payment Record')
    
    @api.onchange('amt_percent')
    @api.multi
    def _onchange_amt_percent(self):
        if self.amt_percent and self.amt_percent > 0:
            if self.payment_id.invoice_ids:
                self.amount = self.payment_id.invoice_ids[0].amount_total * self.amt_percent/100
                
class RegisterWriteoffMulti(models.TransientModel):
    _name = 'writeoff.multi'
    
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    amt_percent = fields.Float(string='Amount(%)', digits=(16,2))
    amount_payment = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    register_id = fields.Many2one('account.register.payments', string='Register Record')
    
    @api.onchange('amt_percent')
    @api.multi
    def _onchange_amt_percent(self):
        if self.amt_percent and self.amt_percent > 0:
            if self.register_id.amount_pay_total:
                self.amount_payment = self.register_id.amount_pay_total * self.amt_percent/100
            