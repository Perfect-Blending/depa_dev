# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.addons.ac_account_thai.models.num2word import num2word
from datetime import *

class AccountPettyPayment(models.Model):
    _name="account.petty.payment"
    _description = "Account Petty Payment"
    _order="name"
    _order = "id desc"

    STATES = [('draft', 'Draft'), ('posted', 'Posted'), ('canceled', 'Canceled')]
    REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    @api.depends('lines', 'company_id', 'date')
    def _amount(self):
        for obj in self:
            obj.amount_untaxed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_total = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_total_signed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_total_company_signed = sum(line.price_unit * line.quantity for line in obj.lines)
            obj.amount_untaxed_signed = sum(line.price_unit * line.quantity for line in obj.lines)

    def _compute_amount_tax(self):
        self.amount_untaxed = sum(line.subtotal for line in self.lines)
        self.amount_tax = sum(line.amount for line in self.vat_lines)
        self.amount_wht = sum(line.amount for line in self.wht_lines)
        self.amount_total = (self.amount_untaxed + self.amount_tax) - self.amount_wht
        self.amount_total_company_signed = self.amount_total
        self.amount_untaxed_signed = self.amount_untaxed
        self.amount_total_signed = self.amount_total
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date,type ="purchase",rate = self.currency_rate)
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

    @api.depends('lines', 'company_id', 'date')
    def _pay_amount(self):
        vals={}
        for petty in self:
            amount_inv=0.0
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

    # @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        journal_id = False
        company = self.env.user.company_id
        journal_id = company.petty_cash_payment_journal_id
        return journal_id


    # @api.model
    def _default_currency(self):
        journal = self._default_journal()
        res = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
        return res

    @api.depends("wht_lines")
    def _assembly_type_other(self):
        partner = False
        for obj in self:
            base_40_1 = base_40_2 = base_40_3 = base_40_4a = base_40_4b_1_1 = base_40_4b_1_2 = base_40_4b_1_3 = base_40_4b_1_4 = base_40_4b_2_1 = base_40_4b_2_2 = base_40_4b_2_3 = base_40_4b_2_4 = base_40_4b_2_5 = base_section_3 = base_other = 0.0
            amount_40_1 = amount_40_2 = amount_40_3 = amount_40_4a = amount_40_4b_1_1 = amount_40_4b_1_2 = amount_40_4b_1_3 = amount_40_4b_1_4 = amount_40_4b_2_1 = amount_40_4b_2_2 = amount_40_4b_2_3 = amount_40_4b_2_4 = amount_40_4b_2_5 = amount_section_3 = amount_other = 0.0
            data_40_1 = data_40_1 = data_40_2 = data_40_3 = data_40_4a = data_40_4b_1_1 = data_40_4b_1_2 = data_40_4b_1_3 = data_40_4b_1_4 = data_40_4b_2_1 = data_40_4b_2_2 = data_40_4b_2_3 = data_40_4b_2_4 = data_40_4b_2_5 = data_section_3 = data_other = ''

            for wht in obj.wht_lines:
                partner = wht.partner_id and wht.partner_id.id or False
                if wht.assessable_type == '40_1':
                    base_40_1 += wht.base
                    amount_40_1 += wht.amount
                    data_40_1 = str(wht.date)+','+str(base_40_1)+','+str(amount_40_1)
                elif wht.assessable_type == '40_2':
                    base_40_2 += wht.base
                    amount_40_2 += wht.amount
                    data_40_2 = str(wht.date)+','+str(base_40_2)+','+str(amount_40_2)
                elif wht.assessable_type == '40_3':
                    base_40_3 += wht.base
                    amount_40_3 += wht.amount
                    data_40_3 = str(wht.date)+','+str(base_40_3)+','+str(amount_40_3)
                elif wht.assessable_type == '40_4a':
                    base_40_4a += wht.base
                    amount_40_4a += wht.amount
                    data_40_4a = str(wht.date)+','+str(base_40_4a)+','+str(amount_40_4a)
                elif wht.assessable_type == '40_4b_1.1':
                    base_40_4b_1_1 += wht.base
                    amount_40_4b_1_1 += wht.amount
                    data_40_4b_1_1 = str(wht.date)+','+str(base_40_4b_1_1)+','+str(amount_40_4b_1_1)
                elif wht.assessable_type == '40_4b_1.2':
                    base_40_4b_1_2 += wht.base
                    amount_40_4b_1_2 += wht.amount
                    data_40_4b_1_2 = str(wht.date)+','+str(base_40_4b_1_2)+','+str(amount_40_4b_1_2)
                elif wht.assessable_type == '40_4b_1.3':
                    base_40_4b_1_3 += wht.base
                    amount_40_4b_1_3 += wht.amount
                    data_40_4b_1_3 = str(wht.date)+','+str(base_40_4b_1_3)+','+str(amount_40_4b_1_3)
                elif wht.assessable_type == '40_4b_1.4':
                    base_40_4b_1_4 += wht.base
                    amount_40_4b_1_4 += wht.amount
                    data_40_4b_1_4 = str(wht.date)+','+str(base_40_4b_1_4)+','+str(amount_40_4b_1_4)
                elif wht.assessable_type == '40_4b_2.1':
                    base_40_4b_2_1 += wht.base
                    amount_40_4b_2_1 += wht.amount
                    data_40_4b_2_1 = str(wht.date)+','+str(base_40_4b_2_1)+','+str(amount_40_4b_2_1)
                elif wht.assessable_type == '40_4b_2.2':
                    base_40_4b_2_2 += wht.base
                    amount_40_4b_2_2 += wht.amount
                    data_40_4b_2_2 = str(wht.date)+','+str(base_40_4b_2_2)+','+str(amount_40_4b_2_2)
                elif wht.assessable_type == '40_4b_2.3':
                    base_40_4b_2_3 += wht.base
                    amount_40_4b_2_3 += wht.amount
                    data_40_4b_2_3 = str(wht.date)+','+str(base_40_4b_2_3)+','+str(amount_40_4b_2_3)
                elif wht.assessable_type == '40_4b_2.4':
                    base_40_4b_2_4 += wht.base
                    amount_40_4b_2_4 += wht.amount
                    data_40_4b_2_4 = str(wht.date)+','+str(base_40_4b_2_4)+','+str(amount_40_4b_2_4)
                elif wht.assessable_type == '40_4b_2.5':
                    base_40_4b_2_5 += wht.base
                    amount_40_4b_2_5 += wht.amount
                    data_40_4b_2_5 = str(wht.date)+','+str(base_40_4b_2_5)+','+str(amount_40_4b_2_5)
                elif wht.assessable_type == 'section_3':
                    base_section_3 += wht.base
                    amount_section_3 += wht.amount
                    data_section_3 += str(wht.date)+','+str(base_section_3)+','+str(amount_section_3)
                elif wht.assessable_type == 'other':
                    base_other += wht.base
                    amount_other += wht.amount
                    data_other = str(wht.date)+','+str(base_other)+','+str(amount_other)+','+str(wht.name)
            obj.assembly_type_other = data_other
            obj.assembly_type_40_1 = data_40_1
            obj.assembly_type_40_2 = data_40_2
            obj.assembly_type_40_3 = data_40_3
            obj.assembly_type_40_4a = data_40_4a
            obj.assembly_type_40_4b_1_1 = data_40_4b_1_1
            obj.assembly_type_40_4b_1_2 = data_40_4b_1_2
            obj.assembly_type_40_4b_1_3 = data_40_4b_1_3
            obj.assembly_type_40_4b_1_4 = data_40_4b_1_4
            obj.assembly_type_40_4b_2_1 = data_40_4b_2_1
            obj.assembly_type_40_4b_2_2 = data_40_4b_2_2
            obj.assembly_type_40_4b_2_3 = data_40_4b_2_3
            obj.assembly_type_40_4b_2_4 = data_40_4b_2_4
            obj.assembly_type_40_4b_2_5 = data_40_4b_2_5
            obj.assembly_type_section_3 = data_section_3
            obj.partner_wht_id = partner

    def _get_amount_word_wht(self):
        for obj in self:
            obj.amount_word_wht = num2word(obj.amount_wht,l='th_TH')


    @api.depends("wht_lines")
    def _amount_base_wht(self):
        amount_base_wht=0.0
        for obj in self:
            for wht in obj.wht_lines:
                amount_base_wht += wht.type_tax_use=="purchase" and wht.base or 0.0
            obj.amount_base_wht = amount_base_wht

    # @api.depends('lines', 'amount_total','paid_total')
    # def _compute_payment_difference(self):
    #     if len(self.lines) == 0:
    #         return
    #     payment_difference = 0.0
    #     if self.lines:
    #         payment_difference += (self.paid_total - self.amount_total)
    #     self.payment_difference = payment_difference

    #Fields
    name = fields.Char('Number', copy=False, default=lambda x: _('New'), index=True, readonly=True)
    date = fields.Date('Doc Date', copy=False, index=True, default=fields.Date.context_today, **REQUIRED)
    employee_id = fields.Many2one("hr.employee", "Employee",index=True, **REQUIRED)
    desc = fields.Char("Description", **OPTIONAL)
    fund_id = fields.Many2one("account.petty.fund","Petty Cash Fund",index=True,**REQUIRED)
    paid_total = fields.Monetary('Paid Total', **REQUIRED)
    currency_id = fields.Many2one('res.currency', string='Currency',index=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
    state = fields.Selection(STATES, "Status", default='draft', readonla=True,index=True,)
    
    create_date = fields.Datetime(string="Creation Date", readonly=True, index=True,)
    write_date = fields.Datetime(string= "Write Date", readonly=True, index=True,)
    partner_id = fields.Many2one("res.partner",string="Partner",index=True,)
    lines = fields.One2many("account.petty.payment.line", "petty_id", "Lines", **OPTIONAL)
    notes = fields.Text("Notes", **OPTIONAL)
    amount_untaxed = fields.Monetary(compute='_amount',string="Untaxed Amount",store=True, readonly=True)
    amount_tax = fields.Float(string="Taxed", readonly=True)
    amount_total = fields.Monetary(compute='_amount',string="Total Amount",store=True, readonly=True)
    amount_inv = fields.Monetary(string="Invoice Total",store=True, readonly=True)
    amount_wht = fields.Float(string="Withholding Tax",store=True, readonly=True)
    amount_to_pay = fields.Monetary(compute='_pay_amount',string="Amount To Pay")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('account.petty.payment'),index=True, **OPTIONAL)
    
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

    journal_id = fields.Many2one("account.journal", "Journal",related='company_id.journal_id',index=True,**REQUIRED)
    account_id = fields.Many2one('account.account', 'Account',related='fund_id.account_id',index=True,domain=[('deprecated', '=', False)],**OPTIONAL)
    move_id = fields.Many2one("account.move", "Journal Entry", readonly=True,index=True,)
    vat_lines = fields.One2many("account.tax.line", "petty_id", "VAT Lines", domain=[('tax_id.tax_group','=','vat')], **OPTIONAL)
    wht_lines = fields.One2many("account.tax.line", "petty_id", "WHT Lines", domain=[('tax_id.tax_group','=','wht')], **OPTIONAL)
    #cash_moves = fields.One2many("account.cash.move", "petty_id", "Cash Moves", **OPTIONAL)
    manual_vat = fields.Boolean("Manual VAT :", **OPTIONAL)
    manual_wht = fields.Boolean("Manual WHT :", **OPTIONAL)

    payment_option = fields.Selection([('without_writeoff', 'No Write-Off'), ('with_writeoff', 'Reconcile with Write-Off')]
        , 'Payment Diff.',default='without_writeoff', required=True, readonly=True, states={'draft': [('readonly', False)]})
    writeoff_amount = fields.Float(compute='_get_writeoff_amount', string='Write-Off Amount', readonly=True)
    type = fields.Selection([("in","In"),("out","Out")],"Type",default='out',required=True,change_default=True,index=True,)
    assembly_type_40_1 = fields.Char("40_1", compute="_assembly_type_other", readonly=True)
    assembly_type_40_2 = fields.Char("40_2", compute="_assembly_type_other", readonly=True)
    assembly_type_40_3 = fields.Char("40_3", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4a = fields.Char("40_4a", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_1_1 = fields.Char("40_4b_1_1", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_1_2 = fields.Char("40_4b_1_2", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_1_3 = fields.Char("40_4b_1_3", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_1_4 = fields.Char("40_4b_1_4", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_2_1 = fields.Char("40_4b_2_1", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_2_2 = fields.Char("40_4b_2_2", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_2_3 = fields.Char("40_4b_2_3", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_2_4 = fields.Char("40_4b_2_4", compute="_assembly_type_other", readonly=True)
    assembly_type_40_4b_2_5 = fields.Char("40_4b_2_5", compute="_assembly_type_other", readonly=True)
    assembly_type_section_3 = fields.Char("40_4b_section_3", compute="_assembly_type_other", readonly=True)
    assembly_type_other = fields.Char("40_4b_other", compute="_assembly_type_other", readonly=True)
    amount_base_wht = fields.Monetary(string='WHT Base', readonly=True, compute='_amount_base_wht')
    amount_word_wht =  fields.Char(string="Amount Word Wht", readonly=True , compute= '_get_amount_word_wht')
    partner_wht_id = fields.Many2one("res.partner", "Partner." , compute="_assembly_type_other", readonly=True)
    payment_difference = fields.Monetary()
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')], default='open', 
        string="Payment Difference Handling", copy=False)
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

    def action_draft(self):
        self.state = 'draft'
        return True

    def action_confirmed(self):
        self.state = 'confirmed'
        return True

    def action_cancel(self):
        for obj in self:
            for wht in obj.wht_lines:
                wht.button_cancel()
            for vat in obj.vat_lines:
                vat.button_cancel()
            cash_move = obj.env['account.cash.move'].search([('petty_id','=',obj.id)])
            cash_move.update({"state":"canceled"})
        self.write({"state":"canceled"})
        return True

    def max_petty_fund(self):
        amt=0.0
        res = 0
        max_amount = self.env['account.petty.fund'].search([('id','=',self.fund_id.id)])
        fund_move = self.env["account.cash.move"].search([('fund_id','=',self.fund_id.id)])
        for move in fund_move:
            if move.state!="posted":
                continue
            if move.type=='in':
                amt += move.amount
            elif move.type=='out':
                amt -= move.amount

        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
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

    def button_posted(self):
        account_name =''

        aref = 'account.petty.payment,%s'%(self.id)

        if self.payment_difference_handling != "reconcile":
            if self.paid_total != round(self.amount_total,2):
                raise UserError(_('Amount Paid Total Incorrect'))
                return
       
        if not self:
            return
        if not account_name:
            seq = self.journal_id.sequence_id.code
            sequence_id = self.env['ir.sequence'].search([('code','=',seq)])
            sequence_id = sequence_id and sequence_id[0] or False
            if sequence_id:
                name = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
            else:
                raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
            account_name = name
        #currency_rate = 1.0
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
        diff_currency = self.currency_id != self.company_id.currency_id
        for obj in self:
            lname = obj.desc or _('Petty Cash Payment')
            lref = obj.name

            ## create cash move
            amount = self._convert_amount(obj.paid_total)
            cash_move_vals = {
                "petty_id": obj.id,
                "fund_id": obj.fund_id.id,
                "amount": amount,
                "account_id":obj.fund_id.account_id.id,
                # 'currency_id': obj.company_id.currency_id.id,
                "type": "out",
                "date": obj.date,
                "name": lref,
                # "notes": lname,
                # "state": "posted",
            }
            self.env["account.cash.move"].create(cash_move_vals)
            vals={
                "name": account_name,
                "ref": obj.name,
                "origin": obj.name,
                "aref":aref,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.company_id.currency_id.id,
                'company_id':obj.company_id.id,
                'line_ids': [],
                'state':'draft',
                'type':'out_invoice',
                "partner_id": self.employee_id.id,
            }
#----------------------------------------------------------
            #wht
            for wht in obj.wht_lines:
                amount = self._convert_amount(round(wht.amount,2))
                lines_vals={
                    "account_id": wht.account_id.id,
                    "price_unit": amount,
                    "name": wht.name,
                }
                vals['line_ids'].append((0, 0, lines_vals))

            #credit
            amount_cre = self._convert_amount(obj.paid_total)
            lines_vals={
                "account_id": obj.fund_id.account_id.id,
                "price_unit": amount_cre,
                "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
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
                    "price_unit": amount_cre,
                }
                vals['line_ids'].append((0, 0, vals_difference))
#----------------------------------------------------------
            #vat
            for vat in obj.vat_lines:
                amount = self._convert_amount(round(vat.amount,2))
                lines_vals={
                    "account_id": vat.account_id.id,
                    "price_unit": amount,
                    "name": vat.name,
                }
                vals['line_ids'].append((0, 0, lines_vals))
                if vat.tax_total and vat.tax_total != 0.0:
                    lines_vals= obj.get_petty_move_lines_vat_distribute(obj.id)
                    vals['line_ids'].append((0, 0, lines_vals))

            #debit
            for line in obj.lines:
                for tax in line.taxes:
                    if  tax.price_include==True:
                        amount = self._convert_amount(line.subtotal)
                        lines_vals={
                            "account_id": line.account_id.id,
                            "price_unit": 0.0,
                            "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                        }
                    elif tax.price_include==False and tax.tax_group == 'vat':
                        amount = self._convert_amount((line.quantity * line.price_unit))
                        lines_vals={
                            "account_id": line.account_id.id,
                            "price_unit": 0.0,
                            "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                        }
                    else :
                        amount = self._convert_amount(round(line.quantity * line.price_unit,2))
                        lines_vals={
                            "account_id": line.account_id.id,
                            "price_unit": 0.0,
                            "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                        }
                if not line.taxes:
                    amount = self._convert_amount(round(line.quantity * line.price_unit,2))
                    lines_vals={
                        "account_id": line.account_id.id,
                        "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                        "price_unit": 0.0,
                    }
                vals['line_ids'].append((0, 0, lines_vals))
#--------------------------------------------------------------
            move_id=self.env["account.move"].create(vals)
            # move_id.invoice_line_ids = lines_vals
            move_id.action_post()
            self.update({"state":"posted",
                         "move_id": move_id.id,
            })

            if obj.vat_lines:
                for vat in obj.vat_lines:
                    vat.update({"move_id": move_id.id,"type_tax_use":"purchase",})

            if obj.wht_lines:
                ref_name = self._set_sequence_wht()
                for wht_line in obj.wht_lines:
                    wht_line.update({"move_id": move_id.id,"ref": ref_name,"type_tax_use":"purchase",})


        return True

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

    def preview_posted(self):
        account_name =''
        if self.payment_difference_handling != "reconcile":
            if self.paid_total != round(self.amount_total,2):
                raise UserError(_('Amount Paid Total Incorrect'))
                return
        # if self.max_petty_fund() == 1:
            return
        if not self:
            return
        account_name = '/'
        #currency_rate = 1.0
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
        diff_currency = self.currency_id != self.company_id.currency_id
        for obj in self:
            vals={
                "name": account_name,
                "ref": obj.name,
                #"origin": obj.name,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id':obj.company_id.id,
                "petty_payment_id": obj.id,
                'state':'posted',
                'line_ids': [],
            }
#----------------------------------------------------------
            #wht
            for wht in obj.wht_lines:
                amount = self._convert_amount(round(wht.amount))
                lines_vals={
                    "account_id": wht.account_id.id,
                    "amount_currency": diff_currency and round(wht.amount,2)*-1,
                    "currency_id": obj.currency_id.id,
                    "petty_payment_id": obj.id,
                    "debit": 0.0,
                    "credit": amount,
                    "name": wht.name,
                    "partner_id": wht.partner_id.id,
                    "date": wht.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))

            #credit
            amount_cre = self._convert_amount(obj.paid_total)
            lines_vals={
                "account_id": obj.fund_id.account_id.id,
                "amount_currency": diff_currency and round(obj.paid_total,2) *-1,
                "currency_id": obj.currency_id.id,
                "petty_payment_id": obj.id,
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
                    "petty_payment_id": obj.id,
                    "amount_currency": diff_currency and round(wo_amt,2),
                    "currency_id": self.currency_id.id,
                    "debit": amount_de,
                    "credit": amount_cre,
                }
                vals['line_ids'].append((0, 0, vals_difference))
#----------------------------------------------------------
            #vat
            #for vat in obj.vat_lines:
                #lines_vals={
                    #"account_id": vat.account_id.id,
                    #"amount_currency": diff_currency and round(vat.amount,2),
                    #"currency_id": obj.currency_id.id,
                    #"petty_payment_id": obj.id,
                    #"debit": round(vat.amount*currency_rate,2),
                    #"credit": 0.0,
                    #"name": vat.name,
                    #"partner_id": vat.partner_id.id,
                    #"ref": vat.ref,
                    #"date": vat.date,
                #}
                #vals['line_ids'].append((0, 0, lines_vals))
            for vat in obj.vat_lines:
                amount = self._convert_amount(round(vat.amount,2))
                lines_vals={
                    "account_id": vat.account_id.id,
                    "amount_currency": diff_currency and round(vat.amount,2),
                    "currency_id": obj.currency_id.id,
                    "petty_payment_id": obj.id,
                    "debit": amount,
                    "credit": 0.0,
                    "name": vat.name,
                    "partner_id": vat.partner_id.id,
                    "ref": vat.ref,
                    "date": vat.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))
                if vat.tax_total and vat.tax_total != 0.0:
                    lines_vals= obj.get_petty_move_lines_vat_distribute_pre(obj.id)
                    vals['line_ids'].append((0, 0, lines_vals))

            #debit
            for line in obj.lines:
                for tax in line.taxes:
                    if  tax.price_include==True:
                        amount = self._convert_amount(line.subtotal)
                        lines_vals={
                            "account_id": line.account_id.id,
                            "amount_currency": diff_currency and round(line.subtotal,2),
                            "currency_id": obj.currency_id.id,
                            "petty_payment_id": obj.id,
                            "debit": amount,
                            "credit": 0.0,
                            "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                            "date": obj.date,
                            "analytic_account_id": line.analytic_account_id.id,
                            #"partner_id": self.employee_id.id,
                        }  
                    elif tax.price_include==False and tax.tax_group == 'vat':
                        amount = self._convert_amount(line.quantity * line.price_unit)
                        lines_vals={
                            "account_id": line.account_id.id,
                            "amount_currency": diff_currency and round(line.quantity * line.price_unit,2),
                            "currency_id": obj.currency_id.id,
                            "petty_payment_id": obj.id,
                            "debit": amount,
                            "credit": 0.0,
                            "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                            "date": obj.date,
                            "analytic_account_id": line.analytic_account_id.id,
                            #"partner_id": self.employee_id.id,
                        }  
                    else :
                        amount = self._convert_amount((line.quantity * line.price_unit))
                        lines_vals={
                            "account_id": line.account_id.id,
                            "amount_currency": diff_currency and round(line.quantity * line.price_unit,2),
                            "currency_id": obj.currency_id.id,
                            "petty_payment_id": obj.id,
                            "debit": amount,
                            "credit": 0.0,
                            "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                            "date": obj.date,
                            #"partner_id": self.employee_id.id,
                            "analytic_account_id": line.analytic_account_id.id,
                        }
                if not line.taxes:
                    amount = self._convert_amount((line.quantity * line.price_unit))
                    lines_vals={
                        "account_id": line.account_id.id,
                        "amount_currency": diff_currency and round(line.quantity * line.price_unit,2),
                        "currency_id": obj.currency_id.id,
                        "petty_payment_id": obj.id,
                        "debit": amount,
                        "credit": 0.0,
                        "name": obj.employee_id and _("Petty Cash payment for ")+obj.employee_id.name or obj.name,
                        "date": obj.date,
                        "analytic_account_id": line.analytic_account_id.id,
                        #"partner_id": self.employee_id.id,
                    }
                vals['line_ids'].append((0, 0, lines_vals))
#--------------------------------------------------------------
            self.env["account.move.preview"].create(vals)
        return True

    def button_preview(self):
        if not self.id:
            raise UserError(_('You cannot data.'))
        else:
            move_preview = self.env['account.move.preview'].search([('petty_payment_id','=',self.id)])
            move_preview_line = self.env['account.move.preview.lines'].search([('petty_payment_id','=',self.id)])
            if not move_preview:
                self.preview_posted()
            else:
                move_preview.unlink()
                move_preview_line.unlink()
                self.preview_posted()
        return {
            'name': _('Preview Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.move.preview.lines',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':"new",
            'context':"{'action_id':active_id}",
            'domain': [('petty_payment_id', '=', self.id)],
        }



    def _set_sequence_wht(self):
        if not self:
            return
        seq = 'wht.purchase'
        sequence_id = self.env['ir.sequence'].search([('code','=',seq)])
        sequence_id = sequence_id and sequence_id[0] or False
        if sequence_id:
            res = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Plase set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
        return res


    def button_cancel(self):
        move_obj = self.env['account.move'].browse(self.move_id.id)
        date_today = fields.Date.today() #datetime.now().strftime("%Y-%m-%d")
        for obj in self:
            if obj.state=='canceled':
                continue

            cancel_date = datetime.strptime(str(date_today),"%Y-%m-%d")
            petty_date = datetime.strptime(str(obj.date),"%Y-%m-%d")

            if petty_date.month < cancel_date.month:
                if obj.vat_lines or obj.wht_lines:
                    raise UserError(_('You cannot cancel an petty cash payment because it is not in the current month.'))

            move = obj.move_id
            # if move:
            #     if move.state=='posted':
            #         move_obj.reverse_moves(date_today,move.journal_id)
            #     else:
            #         move_obj.action_reset(date_today,move.journal_id)
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
            # 'manual': False,
            # 'sequence': tax['sequence'],
            # 'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            'account_id': (tax['account_id'] or line.account_id.id),
            'date':self.date
        }

        return vals

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
                key = self.env['account.tax'].browse(tax['id'])
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

    def button_compute_tax(self):
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        account_tax = self.env['account.tax.line']
        for obj in self:
            if obj.manual_vat:
                return
            # Delete non-manual tax lines
            self._cr.execute("DELETE FROM account_tax_line WHERE  petty_id=%s ", (obj.id,))
            self.invalidate_cache()
            #self._compute_amount_tax()
           # Generate one tax line per tax, however many invoice lines it's applied to
            tax_grouped = obj.get_taxes_values()
            for tax in tax_grouped.values():
                account_tax.create(tax)
            self._compute_amount_tax()

    @api.model
    def create(self, vals):
        payment = super(AccountPettyPayment, self).create(vals)
        payment._set_sequence()
        payment._compute_amount_tax()
        #if payment.paid_total != payment.amount_total:
            #raise UserError(_('Amount Paid Total Incorrect'))
            #return
        # if payment.max_petty_fund()== 1:
            # return
        return payment

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

        res = super(AccountPettyPayment, self).write(vals)
        if not self.lines:
            for vat in self.vat_lines:
                vat.unlink()
            for wht in self.wht_lines:
                wht.unlink()
        return res

    def _set_sequence(self):
        if not self:
           return
        if not self.name or str(self.name).lower() in ('new', '/', False):
            seq = 'petty.cash.payment'
            sequence_id = self.env['ir.sequence'].search([('code','=',seq)])
            sequence_id = sequence_id and sequence_id[0] or False
            if sequence_id:
                ref = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
            else:
                raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
            self.name = ref
        return True

class AccountPettyPaymentLine(models.Model):
    _name = "account.petty.payment.line"
    _description = "Account Petty Payment Lines"

    @api.depends('quantity','price_unit','taxes')
    def _subtotal(self):
        tax_obj = self.env['account.tax']
        result = {}

        for line in self:
            subtotal = line.quantity * line.price_unit
            line.subtotal = subtotal
            line.subtotal_excl =  subtotal
            for  tax in line.taxes:
                result[line.id] = {'subtotal': subtotal, 'subtotal_excl': subtotal}
                if tax.tax_group=='vat':
                    for include in line.taxes:
                        if include.price_include==True:
                            amount = subtotal * (100 /107)
                            line.tax_amount = subtotal - amount
                            line.subtotal = amount
                            line.subtotal_excl =  amount
                        else:
                            line.tax_amount = (subtotal * tax.amount)/100
                            line.subtotal =  subtotal
                            line.subtotal_excl =  subtotal

    @api.depends('taxes')
    def _type_tax(self):
        type_tax = ""
        for obj in self:
            if obj.taxes:
                for tax in obj.taxes:
                    if tax.tax_group == 'vat' :
                        type_tax = "vat"
            obj.type_tax = type_tax
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
    tax_amount = fields.Float(string="TAX",store = True)
    wht_amount = fields.Float(string="WHT",store = True)
    type_tax = fields.Char("type tax",compute ="_type_tax")
    type_wht = fields.Char("type wht",compute ="_type_wht")
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
        res.petty_id.button_compute_tax()
        return res

    def write(self, vals):
        res = super(AccountPettyPaymentLine, self).write(vals)
        if 'price_unit' in vals or 'quantity' in vals or 'taxes' in vals or 'product_id' in vals or 'currency_id' in vals:
            self.petty_id.button_compute_tax()
        return res
