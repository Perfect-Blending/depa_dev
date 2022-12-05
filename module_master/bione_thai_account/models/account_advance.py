# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AdvanceBioneSupplierReceiptsBank(models.Model):
    _inherit = 'bione.supplier.receipts.bank'
    advance_id = fields.Many2one('account.advance', string='Advance', ondeleted='cascade',index=True)

class AdvancePartner(models.Model):
    _inherit = 'hr.employee'
    partner_id = fields.Many2one('res.partner', string='Partner')

class AccountAdvance(models.Model):
    _name = "account.advance"
    _description = 'Advance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    _CONTROL_STATE={"draft":[("readonly",False)]}
    _REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    _OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    @api.one
    @api.depends('lines', 'company_id', 'date')
    def _compute_amount(self):
        self.amount_total = sum(line.amount for line in self.lines)
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_total
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #amount_total_company_signed = self.amount_total * self.currency_rate
            #amount_untaxed_signed = self.amount_total * self.currency_rate
            currency_id = self.currency_id.with_context(date=self.date,type= 'purchase',rate = self.currency_rate)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
        self.amount_total_company_signed = amount_total_company_signed
        self.amount_total_signed =  amount_total_company_signed #self.amount_total
        self.amount_untaxed_signed = amount_untaxed_signed

    def _compute_amount_clear(self):
        amount_remaining = self.amount_total
        amount_clear = 0.0
        clearing = self.env["account.advance.clear"].search([('advance_id', '=', self.id)])
        for clear in clearing:
            if clear.state == "posted":
                amount_remaining -= clear.amount_total + (clear.recv_total - clear.paid_total)
                # print(amount_remaining)
                amount_clear += clear.amount_total#clear.recv_total - clear.paid_total #700
                print(amount_clear)
        if amount_remaining <= 0.0:
            amount_remaining = 0.0
        if amount_clear <= 0.0 or amount_remaining == 0.0:
            amount_clear = 0.0
        # print('================>')
        # print(amount_remaining)
        # print(amount_clear)
        if self.state == "confirmed":
            self.amount_remaining = self.amount_total - amount_clear
            self.amount_clear = amount_clear
        if self.state == "done":
            self.amount_remaining = amount_clear
            self.amount_clear = self.amount_total - amount_clear

    # def _compute_amount_clear(self):
    #     amount_remaining = self.amount_total
    #     amount_clear=0.0
    #     clearing = self.env["account.advance.clear"].search([('advance_id','=',self.id)])
    #     amount_total = 0.0
    #     amount_diff = 0.0
    #     # if self.state in ["confirmed","done"]:
    #
    #     for clear in clearing:
    #         if clear.state=="posted":
    #             recv_total = clear.amount_advance  # clear.recv_total
    #             amount_total += clear.amount_diff  # clear.paid_total
    #             amount_diff +=  clear.amount_total
    #             # amount_remaining -= (clear.amount_advance - clear.paid_total)#(clear.recv_total - clear.paid_total)
    #             amount_clear +=  clear.amount_advance - clear.amount_diff
    #
    #     if amount_remaining <= 0.0:
    #         amount_remaining = 0.0
    #     if amount_clear <= 0.0 or amount_remaining == 0.0:
    #         amount_clear = 0.0
    #     self.amount_remaining = amount_remaining - amount_clear #amount_total # amount_remaining - amount_clear
    #     self.amount_clear = amount_diff #amount_clear

    # @api.multi
    # @api.depends('cash_moves.amount', 'cheques.amount', 'credit_cards.amount', 'banktr_ids.amount', 'banktr_ids.fee_amount')
    # def _paid_amount(self):
    #     for adv in self:
    #         paid_total = paid_cash = paid_cheque = paid_credit_card =  paid_transfer = fee_amount = 0.0
    #         for cm in adv.cash_moves:
    #             paid_cash += self.currency_id.compute(cm.amount, self.company_id.currency_id)
    #         for cq in adv.cheques:
    #             paid_cheque += self.currency_id.compute(cq.amount, self.company_id.currency_id)
    #         for bm in adv.banktr_ids:
    #             paid_transfer += self.currency_id.compute(bm.amount, self.company_id.currency_id)
    #             fee_amount += self.currency_id.compute(bm.fee_amount, self.company_id.currency_id)
    #         for cc in adv.credit_cards:
    #             paid_credit_card += self.currency_id.compute(cc.amount, self.company_id.currency_id)
    #
    #         paid_total = paid_cash + paid_cheque + paid_transfer + paid_credit_card
    #
    #         adv.paid_cheque = paid_cheque
    #         adv.paid_cash = paid_cash
    #         adv.paid_transfer = paid_transfer
    #         adv.paid_credit_card = paid_credit_card
    #         adv.paid_total = paid_total
    #         adv.amount = paid_total

    # @api.model
    # def _default_journal(self):
    #     if self._context.get('default_journal_id', False):
    #         return self.env['account.journal'].browse(self._context.get('default_journal_id'))
    #     journal_id = False
    #     company = self.env.user.company_id
    #     journal_id = company.advance_journal_id
    #     return journal_id
    #
    # @api.model
    # def _default_currency(self):
    #     journal = self._default_journal()
    #     res = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
    #     return res

    def get_count(self):
        for obj in self:
            clear_count = 0
            clear = obj.env['account.advance.clear'].search([('advance_id','=',obj.id)])
            for aucs in clear:
                clear_count += 1
            obj.clear_count = clear_count

    @api.returns('self')
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    @api.multi
    def _get_default_journal(self):
        params = self.env['ir.config_parameter'].sudo()
        return int(params.get_param('bione_thai_account.journal_id', default=False)) or False


    @api.multi
    def _get_default_account(self):
        params = self.env['ir.config_parameter'].sudo()
        return int(params.get_param('bione_thai_account.advance_account_id', default=False)) or False

    # Fields
    name = fields.Char('Number', copy=False, default=lambda x: _('/'), index=True, readonly=True )
    date = fields.Date('Date', copy=False, index=True, default=fields.Date.context_today, **_REQUIRED)
    date_due = fields.Date('Due Date', copy=False, index=True, default=fields.Date.context_today, **_REQUIRED)
    advance_request_id = fields.Many2one('account.advance.request', string='Reference', index=True)
    origin = fields.Char('Source', copy=False, help="Reference of the document that generated this document.", **_OPTIONAL)

    ref = fields.Char(string='Reference', **_OPTIONAL)
    notes = fields.Text(string='Notes', **_OPTIONAL)

    employee_id = fields.Many2one('hr.employee', 'Employee', index=True, **_REQUIRED, default= _default_employee)
    company_id = fields.Many2one('res.company', 'Company', index=True,default=lambda self: self.env.user.company_id, **_REQUIRED)
    # journal_id = fields.Many2one('account.journal', 'Journal',index=True,related='company_id.advance_journal_id', **_REQUIRED)
    journal_id = fields.Many2one('account.journal', 'Journal',index=True, **_REQUIRED,default=_get_default_journal)
    account_id = fields.Many2one('account.account', 'Advance Account',index=True,domain=[('deprecated', '=', False)], **_OPTIONAL,default=_get_default_account)
    # account_id = fields.Many2one('account.account', 'Advance Account',index=True, related='company_id.advance_account_id',domain=[('deprecated', '=', False)], **_OPTIONAL)
    move_id = fields.Many2one('account.move', string='Journal Entry',
        readonly=True, index=True, ondelete='restrict', copy=False,
        help="Link to the automatically generated Journal Items.")
    move_name = fields.Char(string='Journal Entry Name', readonly=False,
        default=False, copy=False,
        help="Technical field holding the number given to the invoice, automatically set when the invoice is validated then stored to set the same number again if the invoice is cancelled, set to draft and re-validated.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('confirmed', 'Waiting for Clear'),
        ('done', 'Cleared'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange', index=True)
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total in Invoice Currency', currency_field='currency_id',
        store=True, readonly=True, compute='_compute_amount',
        help="Total amount in the currency of the invoice, negative for credit notes.")
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount',
        help="Total amount in the currency of the company, negative for credit notes.")
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True,index=True)
    currency_rate = fields.Float("Exchange Rate", readonly=True, states={'draft': [('readonly', False)]}, digits=(12, 6))
    currency_rate_date = fields.Date("Exchange Rate Date", readonly=True, states={'draft': [('readonly', False)]})

    # clear_ids = fields.One2many('account.advance.clear', 'advance_id', string='Advance Clear')
    lines = fields.One2many('account.advance.line', 'advance_id', string='Lines')

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount')
    amount_remaining = fields.Monetary(string='Remaining', readonly=True, compute='_compute_amount_clear')
    amount_clear = fields.Monetary(string='Clear', readonly=True,compute='_compute_amount_clear')

    cash_moves = fields.One2many('account.cash.move', 'advance_id', string='Cash')
    cheques = fields.One2many('bione.cheque', 'advance_id', string='Cheques',)
    # cheque_ids = fields.One2many('bione.cheque', 'supplier_payment_id', string=u'เช็คจ่าย')
    # banktr_ids = fields.One2many('account.bank.move', 'advance_id', string='Transfer',)
    banktr_ids = fields.One2many('bione.supplier.receipts.bank', 'advance_id', string=u'โอน')
    # credit_cards = fields.One2many('account.credit.card', 'advance_id', string='Credit Cards',)
    paid_cash = fields.Monetary(string='Paid Cash', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_cheque = fields.Monetary(string='Paid Cheque', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_transfer = fields.Monetary(string='Paid Transfer', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_credit_card = fields.Monetary(string='Paid Credit Card', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    paid_total = fields.Monetary(string='Paid Total', store=True, readonly=True, compute='_paid_amount', track_visibility='onchange')
    advance_clear_ids = fields.One2many('account.advance.clear', 'advance_id', string='Clearing')
    clear_count = fields.Integer("Count clear", compute="get_count", default=0)

    title_id_advance = fields.Many2one('advance.requisition.title','วัตถุประสงค์',required=False)
    description = fields.Text('รายละเอียด (ถ้ามี)', copy=False, **_OPTIONAL)
    user_id = fields.Many2one('res.users', string='Created by', required=False, default=lambda self: self.env.user)
    user_approve = fields.Many2one('res.users', string='Approved by')
    report_template_id = fields.Many2one('report.html.template', string="หัวข้อรายงาน")
    # Budget details

    # budget_source = fields.Many2one('budget.fund_management', string='งบประมาณ',domain=[('state', '=','success')])
    department = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True, readonly=True)
    payment_method = fields.Selection([('check', 'เช็คฯ'), ('cash', 'เงินสด'), ('bank', 'โอนธนาคาร'), ('etc', 'อื่นๆ')], string='รูปแบบการจ่าย',required=True,default='check')
    payment_voucher_type = fields.Selection([('บค', 'บค.'), ('บย', 'บย.'), ('none', 'ไม่ระบุ')], string='ประเภทใบสำคัญ',required=True,default='none')

    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id or self.env.user.company_id.currency_id

    # @api.onchange('currency_id','date')
    # def onchange_currency_id(self):
    #     currency_id = self.currency_id.id
    #     currency = self.env["res.currency"].browse(currency_id).with_context(date=self.date)
    #     for line in self.lines:
    #         line.currency_id = self.currency_id.id
    #     if currency:
    #         self.currency_rate = currency.rate
    #         self.currency_rate_date = currency.date

    @api.multi
    def print_memo(self):
        # self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env.ref('ac_qweb.action_report_advance_memo').report_action(self)



    @api.multi
    def action_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def action_open(self):
        self.state = 'open'
        return True

    @api.multi
    def action_confirmed(self):
        self.state = 'confirmed'
        return True

    @api.multi
    def action_done(self):
        self.state = 'done'
        return True

    @api.multi
    def action_cancel(self):
        if self.state not in 'draft':
            if self.state in 'confirmed':
                clearing = self.env['account.advance.clear'].search([('advance_id','=',self.id)])
                if clearing:
                    raise UserError(_('Not allow to cancel this document (%s)'%(self.name_get()[0][1])))
                #else:
                    #advance_r = self.env['account.advance.request'].search([('name','=',self.ref)])
                    #if advance_r:
                        #advance_r.update({'state':'draft'})
        self.update({'state':'cancel'})
        return True

    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].with_context(
    #         ir_sequence_date=vals.get('date')).next_by_code('account.advance')
    #     return super(AccountAdvance, self).create(vals)

    @api.multi
    def unlink(self):
        check = [(obj) for obj in self if obj.state not in ('draft') or (obj.name and obj.name != '/')]
        if check:
            raise UserError(_('You cannot delete. You must cancel only.'))
        else:
            return super(AccountAdvance, self).unlink()

    @api.multi
    def button_draft(self):
        self.write({"state": "draft"})
        return True

    @api.multi
    def button_posted(self):
        params = self.env['ir.config_parameter'].sudo()
        move = self.env['account.move']
        diff_currency = self.currency_id != self.company_id.currency_id
        # add fields Referent by model and id
        aref = 'account.advance,%s' % (self.id)

        for obj in self:
            name_sequence = self.env['ir.sequence'].with_context(ir_sequence_date=self.date).next_by_code('account.advance')

            vals = {
                "name": name_sequence,
                "ref": name_sequence,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id': obj.company_id.id,
                'state': 'posted',
                "origin": name_sequence,
                "aref": aref,
                'narration':obj.description,
                'line_ids': [],
                'partner_id': obj.employee_id.partner_id.id or 0,
            }
            # cash payments
            for cash in obj.cash_moves:
                if cash.fund_id:
                    max_amount = obj.env['account.petty.fund'].search([('id', '=', cash.fund_id.id)])
                    amt = obj._check_func(cash.fund_id, cash.amount, cash.type)
                    if amt < 0:
                        raise UserError(_('Petty cash fund exceeding the maximum rate defined. :: amt < 0'))
                    if max_amount.max_amount < amt:
                        raise UserError(
                            _("Petty cash fund exceeding the maximum rate defined.::max_amount(%d) < amt(%d)") % (
                            max_amount.max_amount, amt))

                # credit
                amount = self._convert_amount(cash.amount)
                lines_vals = {
                    "account_id": cash.account_id.id,
                    # "amount_currency": diff_currency and cash.amount * -1,
                    # "currency_id": self.currency_id.id,
                    "debit": 0.0,
                    "credit": amount,
                    "name": obj.employee_id and _("Advance payment for ") + obj.employee_id.name or obj.name,
                    "date": obj.date,
                    'partner_id': obj.employee_id.partner_id.id or 0,
                }
                vals['line_ids'].append((0, 0, lines_vals))
                # if cash.fund_id:
                cash.update({"state": "posted"})
            for bank in obj.banktr_ids:
                # amount = self._convert_amount(bank.amount+trans.fee_amount)
                lines_vals = {
                    "account_id": bank.name.id,
                    # "amount_currency": diff_currency and round(bank.amount, 2),
                    "currency_id": obj.currency_id.id,
                    'debit': bank.amount < 0 and abs(bank.amount) or 0.0,
                    'credit': bank.amount > 0 and abs(bank.amount) or 0.0,
                    "name": obj.employee_id and _("Advance payment for ") + obj.employee_id.name or obj.name,
                    "date": obj.date,
                    "advance_id": obj.id,
                    'partner_id': obj.employee_id.partner_id.id or 0,
                }
                vals['line_ids'].append((0, 0, lines_vals))
            # cheque payments
            for cq in obj.cheques:
                # credit
                account_pay_id = int(
                    params.get_param('bione_thai_account.cheque_purchase_account_id', default=False)) or False,

                amount = self._convert_amount(cq.amount)
                lines_vals = {
                    "account_id": account_pay_id,#cq.account_pay_id.id,
                    # "amount_currency": diff_currency and cq.amount * -1,
                    "currency_id": self.currency_id.id,
                    "debit": 0.0,
                    "credit": amount,
                    "name": obj.employee_id and _("Advance payment for ") + obj.employee_id.name or obj.name,
                    "date": obj.date,
                    'partner_id': obj.employee_id.partner_id.id or 0,
                }
                vals['line_ids'].append((0, 0, lines_vals))
            ##debit
            amount_de = self._convert_amount(self.amount_total)
            lines_vals = {
                "account_id": self.account_id.id,
                # "amount_currency":diff_currency and self.amount_total,
                "currency_id": self.currency_id.id,
                "debit": amount_de,
                "credit": 0.0,
                "name": obj.employee_id and _("Advance payment for ") + obj.employee_id.name or obj.name,
                "date": obj.date,
                'partner_id': obj.employee_id.partner_id.id or 0,
            }
            vals['line_ids'].append((0, 0, lines_vals))
            move_id = self.env["account.move"].create(vals)
            if self.cash_moves:
                self.cash_moves.update({"state": "posted", 'move_id': move_id.id})
            if self.cheques:
                self.cheques.update({'move_id': move_id.id})
            self.update({"state": "confirmed",
                         "move_id": move_id.id,
                         "name":name_sequence,
                         'move_name': move_id.name,
                         })
        return True

    @api.multi
    def button_cancel(self):
        move_obj = self.env['account.move'].browse(self.move_id.id)
        date_today = fields.Date.today()# datetime.now().strftime("%Y-%m-%d")
        for obj in self:
            if obj.state=='cancel':
                continue
            if self.state in 'done':
                advance = self.env['account.advance.clear'].search([('advance_id','=',self.id)])
                if advance.advance_id:
                    if advance.state in 'posted':
                        raise UserError(_('Not allow to cancel this document (%s)'%(self.name_get()[0][1])))
                    elif advance.state in 'draft':
                        advance.state = 'canceled'
            move = obj.move_id
            if move:
                if move.state=='posted':
                    move_obj.reverse_moves(date_today,move.journal_id)
                else:
                    move_obj.action_reset(date_today,move.journal_id)
        self.action_cancel()
        return True

    @api.multi
    def _check_func(self, fund_id,amount,_type):
        amt=0.0
        fund_move = self.env["account.cash.move"].search([('fund_id','=',fund_id.id)])
        for move in fund_move:
            if move.state!="posted":
                continue
            if move.type=='in':
                amt += move.amount
            elif move.type=='out':
                amt -= move.amount
        if _type == 'in':
            amt += amount
        elif _type=='out':
            amt -= amount


        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            #currency_rate = self.currency_rate
            amt = self._convert_amount(amt)# * currency_rate

        return amt

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
            currency_id = advance.currency_id.with_context(date=advance.date,type= 'purchase',rate = advance.currency_rate)
            return currency_id.compute(amount, advance.company_id.currency_id)


    @api.multi
    def preview_move_create(self):
        account_name =''
        if not self:
           return

        account_name = '/'

        #currency_rate = 1.0
        #if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
             #currency_rate = self.currency_rate
        diff_currency = self.currency_id != self.company_id.currency_id

        for obj in self:
            #company_id=obj.company_id.id
            vals={
                "name": account_name,
                "ref": obj.name,
                "journal_id": obj.journal_id.id,
                "date": obj.date,
                'currency_id': obj.currency_id.id,
                'company_id':obj.company_id.id,
                'state':'posted',
                "advance_id": obj.id,
                #"origin": obj.name,
                'line_ids': [],
            }

            # cash payments
            for cash in obj.cash_moves:
                if cash.fund_id:
                    max_amount = obj.env['account.petty.fund'].search([('id','=',cash.fund_id.id)])
                    amt= obj._check_func(cash.fund_id,cash.amount,cash.type)
                    if amt < 0:
                        raise UserError(_('Petty cash fund exceeding the maximum rate defined.:: amt < 0'))
                    if max_amount.max_amount < amt:
                        # raise UserError(_('Petty cash fund exceeding the maximum rate defined.'))
                        raise UserError(_("Petty cash fund exceeding the maximum rate defined.::max_amount(%d) < amt(%d)") % (max_amount.max_amount, amt))
                #credit
                amount = self._convert_amount(cash.amount)
                lines_vals={
                    "account_id": cash.account_id.id,
                    "amount_currency":diff_currency and cash.amount * -1,
                    "currency_id": self.currency_id.id,
                    "debit": 0.0,
                    "advance_id": obj.id,
                    "credit": amount,
                    "name": obj.employee_id and _("Advance payment for ")+obj.employee_id.name or obj.name,
                    "date": obj.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))


            for card in obj.credit_cards:
                amount = self._convert_amount(card.amount)
                #credit
                lines_vals={
                    "account_id": card.account_id.id,
                    "amount_currency":diff_currency and card.amount * -1,
                    "currency_id": self.currency_id.id,
                    "advance_id": obj.id,
                    "debit": 0.0,
                    "credit": amount,
                    "name": obj.employee_id and _("Advance payment for ")+obj.employee_id.name or obj.name,
                    "date": obj.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))

            # bank transfers
            for trans in obj.banktr_ids:
                amount = self._convert_amount(trans.amount+trans.fee_amount)
                #credit
                lines_vals={
                    "account_id": trans.account_id.id,
                    "amount_currency": diff_currency and trans.amount+(trans.fee_amount or 0.0) * -1,
                    "currency_id": self.currency_id.id,
                    "advance_id": obj.id,
                    "debit": 0.0,
                    "credit": amount,
                    #"credit":round((trans.amount+(trans.fee_amount or 0.0))*currency_rate,2),
                    "name": obj.employee_id and _("Advance payment for ")+obj.employee_id.name or obj.name,
                    "date": obj.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))
            # cheque payments
            for cq in obj.cheques:
                #credit
                amount = self._convert_amount(cq.amount)
                lines_vals={
                    "account_id": cq.account_pay_id.id,
                    "amount_currency":diff_currency and cq.amount * -1,
                    "currency_id": self.currency_id.id,
                    "advance_id": obj.id,
                    "debit": 0.0,
                    "credit":amount,
                    "name": obj.employee_id and _("Advance payment for ")+obj.employee_id.name or obj.name,
                    "date": obj.date,
                }
                vals['line_ids'].append((0, 0, lines_vals))

            ##debit
            amount_de = self._convert_amount(obj.amount_total)
            lines_vals={
                "account_id": self.account_id.id,
                "amount_currency":diff_currency and self.amount_total,
                "currency_id": self.currency_id.id,
                "advance_id": obj.id,
                "debit": amount_de,
                #"debit": round(self.amount_total*currency_rate,2),
                "credit": 0.0,
                "name": obj.employee_id and _("Advance payment for ")+obj.employee_id.name or obj.name,
                "date": obj.date,
            }
            vals['line_ids'].append((0, 0, lines_vals))
            self.env["account.move.preview"].create(vals)
        return True

    @api.multi
    def button_preview(self):
        if not self.id:
            raise UserError(_('You cannot data.'))
        else:
            move_preview = self.env['account.move.preview'].search([('advance_id','=',self.id)])
            move_preview_line = self.env['account.move.preview.lines'].search([('advance_id','=',self.id)])

            if not move_preview_line:
                self.preview_move_create()
            else:
                move_preview.unlink()
                move_preview_line.unlink()
                self.preview_move_create()
        return {
            'name': _('Preview Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.move.preview.lines',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':"new",
            'context':"{'action_id':active_id}",
            'domain': [('advance_id', '=', self.id)],
        }

    @api.multi
    def button_get_clear(self):
        return {
            'name': _('Clearing'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.advance.clear',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('advance_id', '=', self.id)],
        }


    def _set_sequence(self):
        if not self:
           return

        if not self.name or str(self.name).lower() in ('new', '/', False):
            seq = 'account.advance'
            sequence_id = self.env['ir.sequence'].search([('code','=',seq),('company_id','=',self.company_id.id)])
            sequence_id = sequence_id and sequence_id[0] or False
            if sequence_id:
                name = sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
            else:
                raise UserError(_('Please set %s sequence (Sequence Code : %s)'%(seq.replace("."," "),seq)))
            self.name = name
        return True


class AccountAdvanceLine(models.Model):
    _name = "account.advance.line"

    advance_id = fields.Many2one('account.advance', 'Advance', required=True,index=True)
    product_id = fields.Many2one("product.product", "Product", required=True, index=True)
    name = fields.Char('Description', required=True,index=True)
    amount = fields.Monetary(string="Amount", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',index=True)
    currency_id = fields.Many2one('res.currency', related='advance_id.currency_id', store=True, related_sudo=False,index=True)
    company_currency_id = fields.Many2one('res.currency', related='advance_id.company_currency_id', readonly=True, related_sudo=False,index=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=False,related='advance_id.currency_id',index=True)





    # @api.multi
    # def _prepare_advance_clear_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
    #     self.ensure_one()
    #     advance = self.advance_id
    #     return {
    #         'name': name,
    #         'product_id': self.product_id.id,
    #         'product_uom': self.product_id.uom_po_id.id,
    #         'product_qty': product_qty,
    #         'price_unit': price_unit,
    #         'taxes_id': [(6, 0, taxes_ids)],
    #         'date_planned': requisition.schedule_date or fields.Date.today(),
    #         'account_analytic_id': self.account_analytic_id.id,
    #         'move_dest_ids': self.move_dest_id and [(4, self.move_dest_id.id)] or []
    #     }

    # advance_clear_id = fields.Many2one('account.advance.clear', 'Advance', required=True,index=True)
    # name = fields.Char('Description', required=True,index=True)
    # account_id = fields.Many2one('account.account', 'Account',required=True,domain=[('deprecated', '=', False)],index=True)
    # analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    # amount = fields.Monetary(string="Amount", required=True)
    # have_receipt =fields.Boolean('Receipt',help="HAVE RECEIPT",default = True)
    # partial_type =fields.Boolean('Partial',help="HAVE PARTIAL")
    # type_tax = fields.Char("type tax",compute ="_type_tax")
    # type_wht = fields.Char("type wht",compute ="_type_wht")
    # taxes = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    # amount_untaxed = fields.Monetary(compute = '_get_amount_untaxed',string="Untaxed Amount" ,store = True)
    # tax_amount = fields.Float(compute = '_get_amount_untaxed',string="Untaxed Amount",store = True)
    # wht_amount = fields.Float(compute = '_get_amount_untaxed',string="Untaxed Amount",store = True)
    # product_id = fields.Many2one("product.product","Product",index=True)
    # currency_id = fields.Many2one('res.currency', string='Currency', required=False, related='advance_clear_id.currency_id',index=True)
