# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AccountPettyReceived(models.Model):
    _name="account.petty.received"
    _description = "Account Petty Received"
    _order="id desc"

    STATES = [('draft', 'Draft'), ('posted', 'Posted'), ('canceled', 'Canceled')]
    REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        journal_id = False
        company = self.env.user.company_id
        journal_id = company.petty_cash_payment_journal_id
        return journal_id

    @api.depends('payment_id')
    def _amount(self):
        for obj in self:
            currency_id = obj.currency_id.with_context(date=obj.date,type ="purchase",rate = obj.currency_rate)
            obj.amount_total_signed = currency_id.compute(obj.amount,obj.company_id.currency_id)
            obj.amount_total_company_signed = currency_id.compute(obj.amount,obj.company_id.currency_id)
            obj.amount_untaxed_signed = currency_id.compute(obj.amount,obj.company_id.currency_id)

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        res = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
        return res

    #Fields
    name = fields.Char('Number', copy=False, default=lambda x: _('New'), index=True, readonly=True)
    date = fields.Date('Doc Date', copy=False, index=True, default=fields.Date.context_today, **REQUIRED)
    create_date = fields.Datetime(string="Creation Date", readonly=True)
    write_date = fields.Datetime(string= "Write Date", readonly=True)
    fund_id = fields.Many2one("account.petty.fund","Petty Cash Fund", required=True, index=True,)
    #employee_id = fields.Many2one("hr.employee", "Employee", **REQUIRED)
    desc = fields.Char("Description", **OPTIONAL)
    notes = fields.Text("Notes", **OPTIONAL)
    state = fields.Selection(STATES, "Status", default='draft', readonla=True,index=True,)
    amount = fields.Monetary('Amount', **REQUIRED)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('account.petty.received'),index=True, **OPTIONAL)
    journal_id = fields.Many2one("account.journal", "Journal",index=True,**REQUIRED)
    move_id = fields.Many2one("account.move", "Journal Entry", readonly=True,index=True,)
    account_id = fields.Many2one('account.account', 'Account',related='fund_id.account_id',domain=[('deprecated', '=', False)],index=True,**REQUIRED)
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},index=True,
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

    other_account_id = fields.Many2one('account.account', 'Other Account',index=True,**REQUIRED)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',index=True)
    type = fields.Selection([("in","In"),("out","Out")],"Type",default='in',required=True,change_default=True,index=True,)
    payment_id = fields.Many2one("account.payment", "Reference", domain=[('state', 'not in',['cancel'])],index=True,**OPTIONAL)
    #ref = fields.Char(string='Reference', readonly=True,related='payment_id.name')
    #cash_moves = fields.One2many("account.cash.move", "received_id", "Cash Moves", **OPTIONAL)

    @api.onchange('currency_id','date')
    def onchange_currency_id(self):
        currency_id = self.currency_id.id
        currency = self.env["res.currency"].browse(currency_id).with_context(date=self.date)
        if currency:
            self.currency_rate = currency.rate
            self.currency_rate_date = currency.date

    @api.onchange('payment_id')
    def onchange_payment(self):
        self.amount = self.payment_id.amount
        self.fund_id = self.payment_id.id
        self.currency_id =self.payment_id.currency_id.id,
        # self.currency_rate = self.payment_id.currency_rate
        #self.currency_rate_date = self.payment_id.currency_rate_date,

    def action_draft(self):
        self.state = 'draft'
        return True

    def action_confirmed(self):
        self.state = 'confirmed'
        return True

        self.write({"state":"canceled"})
        cash_move = obj.env['account.cash.move'].search([('petty_id','=',self.id)])
        if cash_move:
            cash_move.update({"state":"canceled"})
        return True

    def check_value_balance(self):
        current_balance =0
        value_balance = self.env['account_petty_fund'].search([('fund_id','=',self.fund_id.id)])
        if value_balance:
            balances = self.env['account_cash_move'].search([('fund_id','=',self.fund_id.id)])
            if balance:
                for balance in balances:
                    if balance.type=="in":
                        current_balance += balance.amount
                    elif balance.type=="out":
                        current_balance -= balance.amount
        if value_balance < current_balance:
            raise UserError(_('You cannot '))
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

    def button_posted(self):
        account_name =''

        #add fields Referent by model and id
        aref = 'account.petty.received,%s'%(self.id)
        lines_vals = []
        if self.amount == 0.0:
            raise UserError(_('Not Amount 0.0 '))
        if not self:
            return
        if not account_name:
            seq = self.journal_id.sequence_id.code
            sequence_id = self.env['ir.sequence'].search([('code','=',seq),('company_id','=',self.company_id.id)])
            sequence_id = sequence_id and sequence_id[0] or False
            if sequence_id:
                name = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
            else:
                raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
            account_name = name

        max_amount = self.env['account.petty.fund'].search([('id','=',self.fund_id.id)])
        amt=0.0
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
            amt += self._convert_amount(self.amount) # * currency_rate
        else:
            amt += self.amount
        if amt < 0:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
        if max_amount.max_amount < amt:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))

        #currency_rate = 1.0
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
        diff_currency =self.currency_id != self.company_id.currency_id
        for obj in self:
            #company_id=obj.company_id.id
            lname = obj.desc or _('Petty Cash Received')
            lref = obj.name

            ## create cash move
            amount = self._convert_amount(obj.amount)
            cash_move_vals = {
                # "received_id": obj.id,
                "fund_id": obj.fund_id.id,
                "amount": amount,
                "account_id":obj.fund_id.account_id.id,
                "type": obj.type,
                "date": obj.date,
                "name": lref,
                # "notes": lname,
                "state": "draft",
            }
            self.env["account.cash.move"].create(cash_move_vals)
            vals={
                "name": account_name,
                "ref": obj.name,
                "origin": obj.name,
                "aref":aref,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id':obj.company_id.id,
                'state':'draft',
                'partner_id':obj.payment_id.partner_id.id,
                'line_ids': [],
                'type':'out_invoice',
            }
            #credit
            amount_cre = self._convert_amount(obj.amount)
            lines_vals.append((0,0,{
                    "account_id": obj.other_account_id.id,
                    "currency_id": obj.currency_id.id,
                    "price_unit": amount_cre,
                    "name":obj.name,
                }))
            # lines_vals={
            #     "account_id": obj.other_account_id.id,
            #     # "amount_currency": diff_currency and round(obj.amount,2) *-1,
            #     "currency_id": obj.currency_id.id,
            #     # "debit": 0.0,
            #     # "credit":amount_cre ,
            #     "name": obj.name,
            #     # "date": obj.date,
            # }
            # vals['line_ids'].append((0, 0, lines_vals))
            #debit
            amount_de = self._convert_amount(obj.amount)
            lines_vals.append((0,0,{
                    "account_id": obj.account_id.id,
                    "currency_id": obj.currency_id.id,
                    "price_unit": amount_de,
                    "name":obj.name,
                }))
            # lines_vals={
            #     "account_id": obj.account_id.id,
            #     "amount_currency": diff_currency and round(obj.amount,2),
            #     "currency_id": obj.currency_id.id,
            #     "debit": amount_de,
            #     "credit": 0.0,
            #     "name": obj.name,
            #     "date": obj.date,
            # }
            move_id=self.env["account.move"].create(vals)
            move_id.invoice_line_ids = lines_vals
            move_id.action_post()
            self.update({"state":"posted",
                         "move_id": move_id.id,
                         "date":move_id.date,
            })
        return True

    def preview_posted(self):
        account_name =''
        if self.amount == 0.0:
            raise UserError(_('Not Amount 0.0 '))
        if not self:
            return
        account_name = '/'

        max_amount = self.env['account.petty.fund'].search([('id','=',self.fund_id.id)])
        amt=0.0
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
            amt += self._convert_amount(self.amount)
        else:
            amt += self.amount

        if amt < 0:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
        if max_amount.max_amount < amt:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))

        #currency_rate = 1.0
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
        diff_currency =self.currency_id != self.company_id.currency_id
        for obj in self:

            vals={
                "name": account_name,
                #"ref": obj.name,
                #"origin": obj.name,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id':obj.company_id.id,
                'state':'draft',
                "petty_received_id":obj.id,
                'line_ids': [],
            }
            #credit
            amount_cre = self._convert_amount(obj.amount)
            lines_vals={
                "account_id": obj.other_account_id.id,
                "amount_currency": diff_currency and round(obj.amount,2) *-1,
                "currency_id": obj.currency_id.id,
                "petty_received_id":obj.id,
                "debit": 0.0,
                "credit": amount_cre,
                "name": obj.name,
                "date": obj.date,
            }
            vals['line_ids'].append((0, 0, lines_vals))
            #debit
            amount_de = self._convert_amount(obj.amount)
            lines_vals={
                "account_id": obj.account_id.id,
                "amount_currency": diff_currency and round(obj.amount,2),
                "currency_id": obj.currency_id.id,
                "petty_received_id":obj.id,
                "debit":amount_de,
                "credit": 0.0,
                "name": obj.name,
                "date": obj.date,
            }
            vals['line_ids'].append((0, 0, lines_vals))
            self.env["account.move.preview"].create(vals)
        return True

    def button_preview(self):
        if not self.id:
            raise UserError(_('You cannot data.'))
        else:
            move_preview = self.env['account.move.preview'].search([('petty_received_id','=',self.id)])
            move_preview_line = self.env['account.move.preview.lines'].search([('petty_received_id','=',self.id)])
            if not move_preview_line:
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
            'domain': [('petty_received_id', '=', self.id)],
        }


    def button_cancel(self):
        date =fields.Date.today()
        if not self:
           return

        for apc in self:
            apc.state = 'canceled'
        return True


    @api.model
    def create(self, vals):
        received = super(AccountPettyReceived, self).create(vals)
        if received.amount == 0.0:
            raise UserError(_('Not Amount 0.0 '))
        received._set_sequence()

        max_amount = received.env['account.petty.fund'].search([('id','=',received.fund_id.id)])
        amt=0.0
        fund_move = received.env["account.cash.move"].search([('fund_id','=',received.fund_id.id)])
        for move in fund_move:
            if move.state!="posted":
                continue
            if move.type=='in':
                amt += move.amount
            elif move.type=='out':
                amt -= move.amount
        if received.currency_id and received.company_id and received.currency_id != received.company_id.currency_id:
            #currency_rate = self.currency_rate
            amt += self._convert_amount(received.amount)
        else:
            amt += received.amount

        if amt < 0:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
        if max_amount.max_amount < amt:
            raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))

        return received

    def _set_sequence(self):
        if not self:
           return
        if not self.name or str(self.name).lower() in ('new', '/', False):
            seq = 'petty.cash.received'
            sequence_id = self.env['ir.sequence'].search([('code','=',seq)])
            sequence_id = sequence_id and sequence_id[0] or False
            if sequence_id:
                ref = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
            else:
                raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
            self.name = ref
        return True

    def unlink(self):
        check = [(obj) for obj in self if obj.state not in ('draft') or (obj.name and obj.name != '/')]
        if check:
            raise UserError(_('You cannot delete. You must cancel only.'))
        else:
            return super(AccountPettyReceived, self).unlink()
