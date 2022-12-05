# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import datetime, timedelta

class AdvanceAccountPettyPaymentTax(models.Model):
    _inherit = 'bione.account.vat'
    petty_id = fields.Many2one('account.petty.payment', string='PettyPayment', ondeleted='cascade', index=True)

class AdvanceAccountPettyPaymentwht(models.Model):
    _inherit = 'bione.wht'
    petty_id = fields.Many2one('account.petty.payment', string='PettyPayment', ondeleted='cascade', index=True)


class AccountPettyPayment(models.Model):
    _name="account.petty.payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order="name"
    _order = "id desc"

    STATES = [('draft', 'Draft'), ('posted', 'Posted'), ('canceled', 'Canceled')]
    REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    @api.multi
    @api.depends('lines', 'company_id', 'date','wht_lines','vat_lines')
    def _amount(self):
        for obj in self:
            obj.amount_untaxed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_tax = sum(line.amount_tax for line in obj.vat_lines)
            obj.amount_total = sum(line.price_unit * line.quantity for line in obj.lines) + sum(line.amount_tax for line in obj.vat_lines) - sum(line.tax for line in obj.wht_lines)
            obj.amount_total_signed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_total_company_signed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_untaxed_signed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_wht = sum(line.tax for line in obj.wht_lines)

    @api.multi
    @api.depends('lines', 'company_id', 'date')
    def _pay_amount(self):
        vals={}
        for petty in self:
            amount_inv=petty.amount_total
            amount_wht=0.0
            #for wht in petty.wht_lines:
                #amount_wht+=wht.wht_amount
            vals[petty.id]={
                "amount_inv": round(amount_inv, 2),
                "amount_wht": round(amount_wht, 2),
                "amount_to_pay": round(amount_inv-amount_wht, 2),
            }
        return vals


    def _get_writeoff_amount(self):
        vals={}
        for obj in self:
            vals[obj.id]=obj.paid_total-obj.amount_to_pay
        return vals

    @api.model
    def _default_journal(self):
        params = self.env['ir.config_parameter'].sudo()
        return int(params.get_param('bione_thai_account.petty_cash_payment_journal_id', default=False)) or False


    @api.model
    def _default_currency(self):
        return self.company_id.currency_id or self.env.user.company_id.currency_id

    @api.one
    @api.depends('lines', 'amount_total','paid_total')
    def _compute_payment_difference(self):
        if len(self.lines) == 0:
            return
        payment_difference = 0.0
        if self.lines:
            payment_difference += (self.paid_total - self.amount_total)

        self.payment_difference = payment_difference


    @api.returns('self')
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    @api.depends('wht_lines')
    def _get_wht(self):
        for obj in self:
            obj.amount_wht = sum(line.tax for line in obj.wht_lines)

    @api.multi
    @api.depends('vat_lines')
    def _get_vat(self):
        for obj in self:
            obj.amount_tax = sum(line.amount_tax for line in obj.vat_lines)

    #Fields
    name = fields.Char('Number', copy=False, default=lambda x: _('New'), index=True, readonly=True)
    date = fields.Date('Doc Date', copy=False, index=True, default=fields.Date.context_today, **REQUIRED)
    create_date = fields.Datetime(string="Creation Date", readonly=True, index=True)
    write_date = fields.Datetime(string= "Write Date", readonly=True, index=True,)
    fund_id = fields.Many2one("account.petty.fund","Petty Cash Fund",index=True,**REQUIRED, track_visibility='onchange')
    employee_id = fields.Many2one("hr.employee", "Employee",index=True, **REQUIRED,default=_default_employee,track_visibility='onchange')
    partner_id = fields.Many2one("res.partner",string="Partner",index=True,)
    desc = fields.Char("Description", **OPTIONAL)
    lines = fields.One2many("account.petty.payment.line", "petty_id", "Lines", **OPTIONAL)
    notes = fields.Text("Notes", **OPTIONAL)
    state = fields.Selection(STATES, "Status", default='draft', readonla=True,index=True, track_visibility='onchange')
    paid_total = fields.Monetary('Paid Total', **REQUIRED,track_visibility='onchange')
    amount_untaxed = fields.Monetary(compute='_amount',string="Untaxed Amount",store=True, readonly=True)
    amount_tax = fields.Float(string="Taxed", compute='_get_vat',track_visibility='onchange',copy=False)
    amount_total = fields.Monetary(compute='_amount',string="Total Amount",store=True, readonly=True)
    amount_inv = fields.Monetary(compute='_pay_amount',string="Invoice Total",store=True, readonly=True)
    amount_wht = fields.Float(string="Withholding Tax", track_visibility='onchange',compute='_get_wht', copy=False)
    amount_to_pay = fields.Monetary(compute='_pay_amount',string="Amount To Pay")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('account.petty.payment'),index=True, **OPTIONAL)
    currency_id = fields.Many2one('res.currency', string='Currency',index=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True,index=True,)
    currency_rate = fields.Float("Exchange Rate", readonly=True, states={'draft': [('readonly', False)]}, digits=(12, 6))
    currency_rate_date = fields.Date("Exchange Rate Date", readonly=True, states={'draft': [('readonly', False)]})
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_amount')
    amount_total_signed = fields.Monetary(string='Total in Currency', currency_field='currency_id',
        store=True, readonly=True, compute='_amount',
        help="Total amount in the currency .")
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_amount',
        help="Total amount in the currency .")
    journal_id = fields.Many2one("account.journal", "Journal",
                                 index=True, **REQUIRED, default=_default_journal)
    account_id = fields.Many2one('account.account', 'Account', index=True,
                                 domain=[('deprecated', '=', False)], **OPTIONAL)

    move_id = fields.Many2one("account.move", "Journal Entry", readonly=True,index=True,)
    vat_lines = fields.One2many('bione.account.vat', 'petty_id', string=u'ภาษีซื้อ')
    wht_lines = fields.One2many('bione.wht', 'petty_id', string=u'ภาษีหัก ณ ที่จ่าย')

    #cash_moves = fields.One2many("account.cash.move", "petty_id", "Cash Moves", **OPTIONAL)
    manual_vat = fields.Boolean("Manual VAT :", **OPTIONAL)
    manual_wht = fields.Boolean("Manual WHT :", **OPTIONAL)

    payment_option = fields.Selection([('without_writeoff', 'No Write-Off'), ('with_writeoff', 'Reconcile with Write-Off')]
        , 'Payment Difference',default='without_writeoff', required=True, readonly=True, states={'draft': [('readonly', False)]})
    writeoff_amount = fields.Float(compute='_get_writeoff_amount', string='Write-Off Amount', readonly=True)
    type = fields.Selection([("in","In"),("out","Out")],"Type",default='out',required=True,change_default=True,index=True,)
    amount_base_wht = fields.Monetary(string='WHT Base', readonly=True, compute='_amount_base_wht')
    # amount_word_wht =  fields.Char(string="Amount Word Wht", readonly=True , compute= '_get_amount_word_wht')
    # partner_wht_id = fields.Many2one("res.partner", "Partner" , compute="_assembly_type_other", readonly=True)
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True,)
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')], default='open', string
="Payment Difference", copy=False)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default='Write-Off')

    @api.onchange('currency_id','date')
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

    @api.multi
    def action_cancel(self):
        # for obj in self:
        #     for wht in obj.wht_lines:
        #         wht.button_cancel()
        #     for vat in obj.vat_lines:
        #         vat.button_cancel()
        #     cash_move = obj.env['account.cash.move'].search([('petty_id','=',obj.id)])
        #     cash_move.update({"state":"canceled"})
        self.write({"state":"canceled"})
        return True

    @api.multi
    def max_petty_fund(self):
        amt=0.0
        res = 0
        max_amount = self.env['account.petty.fund'].search([('id', '=', self.fund_id.id)])
        aml_env = self.env['account.move.line']

        # aml = aml_env.search([('partner_id', '=', self.partner_id.id),
        #                       ('account_id', '=', self.account_id.id)])
        aml = aml_env.search([('account_id', '=', self.fund_id.account_id.id)])
        balance = sum([line.debit - line.credit for line in aml])
        amt = balance
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
            # print(self.paid_total)
            amt -= self._convert_amount(self.paid_total)
        else:
            amt -= self.paid_total

        if amt < 0:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
            res= 1
        if max_amount.max_amount < amt:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
            res= 1

        return res

    @api.multi
    def button_posted(self):

        #add fields Referent by model and id
        aref = 'account.advance.clear,%s'%(self.id)
        sequence_name = self.env['ir.sequence'].next_by_code('account.petty.payment')
        if self.payment_difference_handling != "reconcile":
            if self.paid_total != round(self.amount_total,2):
                raise UserError(_('Amount Paid Total Incorrect'))
                return
        if self.max_petty_fund() == 1:
            return
        if not self:
            return
        #currency_rate = 1.0
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
        diff_currency = self.currency_id != self.company_id.currency_id
        params = self.env['ir.config_parameter'].sudo()
        vat_account_id = int(params.get_param('bione_thai_account.vat_purchase_account_id', default=False)) or False,
        for obj in self:
            lname = obj.desc or _('Petty Cash Payment ')
            lref = obj.name
            # create cash move
            # amount = self._convert_amount(obj.paid_total)
            # cash_move_vals = {
            #     "petty_id": obj.id,
            #     "fund_id": obj.fund_id.id,
            #     "amount": amount,
            #     "account_id": obj.fund_id.account_id.id,
            #     'currency_id': obj.currency_id.id,
            #     "type": "out",
            #     "date": obj.date,
            #     "name": lref,
            #     "notes": lname,
            #     "state": "posted",
            # }
            # self.env["account.cash.move"].create(cash_move_vals)
            vals={
                "name": sequence_name,
                "ref": sequence_name,
                "origin": sequence_name,
                "aref":aref,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id':obj.company_id.id,
                'state':'posted',
                'line_ids': [],
                "narration": obj.desc,
            }
            #----------------------------------------------------------
            #wht
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

                lines_vals={
                    "account_id": wht_account_id,
                    "amount_currency": diff_currency and round(wht.amount,2)*-1,
                    "currency_id": obj.currency_id.id,
                    "debit": 0.0,
                    "credit": wht.tax,
                    "name": wht.name,
                    "partner_id": wht.partner_id.id,
                    # "date": wht.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))
            #credit
            amount_cre = self._convert_amount(obj.paid_total)
            lines_vals={
                "account_id": obj.fund_id.account_id.id,
                "amount_currency": diff_currency and round(obj.paid_total,2) *-1,
                "currency_id": obj.currency_id.id,
                "debit": 0.0,
                "credit": amount_cre,
                "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                #"partner_id": self.employee_id.id,
                "date": obj.date,
            }
            vals['line_ids'].append((0, 0, lines_vals))
            # Make write-off entry
            if self.payment_difference and self.payment_difference_handling=='reconcile':
                wo_amt = round(self.payment_difference,2)
                debit = wo_amt>0 and abs(wo_amt) or 0.0
                credit = wo_amt<0 and abs(wo_amt) or 0.0
                amount_de = self._convert_amount(debit)
                amount_cre = self._convert_amount(credit)
                vals_difference ={
                    "account_id": self.writeoff_account_id.id,
                    "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                    "date": obj.date,
                    "amount_currency": diff_currency and round(wo_amt,2),
                    "currency_id": self.currency_id.id,
                    "debit": amount_de,
                    "credit": amount_cre,
                }
                vals['line_ids'].append((0, 0, vals_difference))
            #----------------------------------------------------------
            #vat
            for vat in obj.vat_lines:
                amount = self._convert_amount(round(vat.amount_tax,2))
                lines_vals={
                    "account_id": vat_account_id,
                    "amount_currency": diff_currency and round(vat.amount_tax,2),
                    "currency_id": obj.currency_id.id,
                    "debit": amount,
                    "credit": 0.0,
                    "name": vat.name,
                    "partner_id": vat.partner_id.id,
                    # "ref": vat.ref,
                    # "date": vat.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))
                # if vat.tax_total and vat.tax_total != 0.0:
                #     lines_vals= obj.get_petty_move_lines_vat_distribute(obj.id)
                #     vals['line_ids'].append((0, 0, lines_vals))

            #debit
            for line in obj.lines:
                amount = self._convert_amount(round(line.quantity * line.price_unit,2))
                lines_vals={
                    "account_id": line.account_id.id,
                    "amount_currency": diff_currency and round(line.quantity * line.price_unit,2),
                    "currency_id": obj.currency_id.id,
                    'credit': amount < 0 and abs(amount) or 0.0,
                    'debit': amount > 0 and abs(amount) or 0.0,
                    "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                    "date": obj.date,
                    "analytic_account_id": line.analytic_account_id.id,
                    #"partner_id": self.employee_id.id,
                }
                vals['line_ids'].append((0, 0, lines_vals))
            #--------------------------------------------------------------
            # print(obj.desc)
            # print(obj)
            move_id=self.env["account.move"].create(vals)
            self.update({
                "name": sequence_name,
                "state": "posted",
                 "move_id": move_id.id,
            })

        return True

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
        for petty in self:
            currency_id = petty.currency_id.with_context(date=petty.date,type= 'purchase',rate = petty.currency_rate)
            return currency_id.compute(amount, petty.company_id.currency_id)

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

    @api.multi
    def button_cancel(self):
        move_obj = self.env['account.move'].browse(self.move_id.id)
        date_today = datetime.now().strftime("%Y-%m-%d")

        for obj in self:
            if obj.state=='canceled':
                continue
            cancel_date = datetime.strptime(date_today,"%Y-%m-%d")
            # petty_date = datetime.strptime(obj.date,"%Y-%m-%d")
            if obj.date.month < cancel_date.month:
                if obj.vat_lines or obj.wht_lines:
                    raise UserError(_('You cannot cancel an petty cash payment because it is not in the current month.'))

            move = obj.move_id
            if move:
                if move.state=='posted':
                    move_obj.reverse_moves(date_today,move.journal_id)
                else:
                    move_obj.action_reset(date_today,move.journal_id)
        self.action_cancel()
        return True

    def _prepare_tax_line_vals(self, line, tax):
        """ Prepare values to create an account.invoice.tax line
        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = {
            'petty_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            'account_id': (tax['account_id'] or line.account_id.id),
            'date':self.date
        }

        return vals

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        amount = 0.0
        #for line in self.lines:
            #amount += (line.price_unit * line.quantity)
        for line in self.lines:
            taxs = 0.0
            for t in line.taxes:
                if t.price_include==True:
                    taxs = line.tax_amount

            taxes = line.taxes.compute_all((line.price_unit * line.quantity) - taxs, self.currency_id)['taxes']
            #amount += (line.price_unit * line.quantity)
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                tax_id = self.env['account.tax'].search([('id', '=', val['tax_id'])])
                amount = (line.price_unit * line.quantity)
                for include in tax_id:
                    if include.price_include==True:
                        val['amount'] = amount - ((line.price_unit * line.quantity) - taxs)
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    @api.multi
    def _compute_amount_tax(self):
        self.amount_untaxed = sum(line.subtotal for line in self.lines)
        self.amount_tax = sum(line.amount_tax for line in self.vat_lines)
        self.amount_wht = sum(line.tax for line in self.wht_lines)
        self.amount_total = (self.amount_untaxed + self.amount_tax) - self.amount_wht
        self.amount_total_company_signed = self.amount_total
        self.amount_untaxed_signed = self.amount_untaxed
        self.amount_total_signed = self.amount_total
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date, type="purchase", rate=self.currency_rate)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
            self.amount_total_company_signed = amount_total_company_signed
            self.amount_unaxed_signed = amount_untaxed_signed
            self.amount_total_signed = self.amount_total_company_signed

        if not self.lines:
            self.amount_untaxed = 0.0
            self.amount_total = 0.0
            self.amount_tax = 0.0
            self.amount_wht = 0.0
            self.amount_total_company_signed = 0.0
            self.amount_unaxed_signed = 0.0
            self.amount_total_signed = 0.0

    @api.model
    def create(self, vals):

        payment = super(AccountPettyPayment, self).create(vals)
        payment._compute_amount_tax()
        if payment.max_petty_fund()== 1:
            return
        return payment

    # @api.multi
    # def write(self, vals):
    #     print(vals)
    #     payment = super(AccountPettyPayment, self).write(vals)
    #     # payment._compute_amount_tax()
    #     # print(payment)
    #     # payment._compute_amount_tax()
    #     # if payment.max_petty_fund() == 1:
    #     #     return
    #     self._compute_amount_tax()
    #     return payment

class AccountPettyPaymentLine(models.Model):
    _name = "account.petty.payment.line"

    @api.depends('quantity','price_unit','taxes')
    def _subtotal(self):
        tax_obj = self.env['account.tax']
        result = {}

        for line in self:
            subtotal = line.quantity * line.price_unit
            line.subtotal = subtotal
            line.subtotal_excl =  subtotal
            # for  tax in line.taxes:
            #     result[line.id] = {'subtotal': subtotal, 'subtotal_excl': subtotal}
            #     if tax.tax_group=='vat':
            #         for include in line.taxes:
            #             if include.price_include==True:
            #                 amount = subtotal * (100 /107)
            #                 line.tax_amount = subtotal - amount
            #                 line.subtotal = amount
            #                 line.subtotal_excl =  amount
            #             else:
            #                 line.tax_amount = (subtotal * tax.amount)/100
            #                 line.subtotal =  subtotal
            #                 line.subtotal_excl =  subtotal

    @api.depends('taxes')
    def _type_tax(self):
        type_tax = ""
        # for obj in self:
        #     if obj.taxes:
        #         for tax in obj.taxes:
        #             if tax.tax_group == 'vat' :
        #                 type_tax = "vat"
        #     obj.type_tax = type_tax
        return type_tax

    @api.depends('taxes')
    def _type_wht(self):
        for obj in self:
            type_wht = ""
            if obj.taxes:
                for tax in obj.taxes:
                    if tax.tax_group in ('wht'):
                        type_wht = "wht"
            obj.type_wht = type_wht
        return type_wht

    name = fields.Char('Description', required=True)
    petty_id = fields.Many2one("account.petty.payment","Payment", required=True, index=True)
    product_id = fields.Many2one("product.product","Product",index=True)
    account_id = fields.Many2one("account.account","Account",required=True,domain=[('deprecated', '=', False)],index=True)
    price_unit = fields.Monetary("Unit Price",required=True)
    quantity = fields.Float("Quantity",default=1)
    subtotal = fields.Monetary(compute='_subtotal', string="Subtotal",store=True, readonly=True)
    subtotal_excl = fields.Monetary(compute='_subtotal', string="Subtotal (Tax excl.)",store=True, readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',index=True)
    tax_amount = fields.Float(compute = '_subtotal',string="TAX",store = True)
    wht_amount = fields.Float(compute = '_subtotal',string="WHT",store = True)
    # type_tax = fields.Char("type tax",compute ="_type_tax")
    # type_wht = fields.Char("type wht",compute ="_type_wht")
    taxes = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    currency_id = fields.Many2one('res.currency', string='Currency', required=False, related='petty_id.currency_id',index=True)

    @api.onchange('product_id')
    def onchange_product(self):
        if not self.product_id:
            return {}
        prod=self.env["product.product"].browse(self.product_id.id)
        vals={
            "name": prod.name,
            "account_id": prod.product_tmpl_id.property_account_expense_id.id or prod.categ_id.property_account_expense_categ_id.id,
            "taxes": [t.id for t in prod.supplier_taxes_id],
        }
        self.name = self.product_id.id
        return {"value": vals}


    @api.model
    def create(self, vals):
        res = super(AccountPettyPaymentLine, self).create(vals)
        # res.petty_id.button_compute_tax()
        return res

    # @api.multi
    # def write(self, vals):
    #     res = super(AccountPettyPaymentLine, self).write(vals)
    #     # if 'price_unit' in vals or 'quantity' in vals or 'taxes' in vals or 'product_id' in vals or 'currency_id' in vals:
    #     #     self.petty_id.button_compute_tax()
    #     return res
