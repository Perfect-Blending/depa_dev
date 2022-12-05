# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import json
import re
import uuid

from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.osv import expression
from odoo.addons import decimal_precision as dp
import logging

# class AccountInvoicePartner(models.Model):
#     _inherit = 'res.partner'
#     @api.model
#     def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
#         print(self.env)
#         print(self.env.context)
#         if self.env.context.get('action_mode',False) == 'petty_received':
#             args = args or []
#             partner_ids = []
#             for partner_ids_petty in  self.env['account.petty.fund'].search([]):
#                 partner_ids.append(partner_ids_petty.partner_id.id)
#             args = args + [('id', 'in', partner_ids)]
#
#         return super(AccountInvoicePartner, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_is_petty_cash(self):
        if self.env.context.get('action_mode',False) == 'petty_received':
            return True
        return False

    billing_id = fields.Many2one('bione.billing', string=u'ใบวางบิล', copy=False)
    deposit_ids = fields.One2many('bione.customer.payment.deposit', 'invoice_id', string=u'มัดจำ')
    supplier_deposit_ids = fields.One2many('bione.supplier.payment.deposit', 'invoice_id', string=u'จ่ายมัดจำ')
    vat_ids = fields.One2many('bione.account.vat', 'supplier_payment_id', string=u'ภาษีซื้อ')
    pfb_old_seq_dn_cn = fields.Char(string=u'บันทึกเลขรันเอกสารเดิม', copy=False)

    # amount_tax = fields.Monetary(string='Tax',
    #                              store=True, compute='_compute_amount_vat')

    # @api.one
    # @api.onchange('amount_tax')
    # def _compute_amount_vat(self):
    #     # round_curr = self.currency_id.round
    #     # self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     # self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
    #     self.amount_total = self.amount_untaxed + self.amount_tax
    #     # amount_total_company_signed = self.amount_total
    #     # amount_untaxed_signed = self.amount_untaxed
    #     # if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
    #     #     currency_id = self.currency_id
    #     #     amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
    #     #                                                        self.company_id,
    #     #                                                        self.date_invoice or fields.Date.today())
    #     #     amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
    #     #                                                  self.company_id, self.date_invoice or fields.Date.today())
    #     # sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #     # self.amount_total_company_signed = amount_total_company_signed * sign
    #     # self.amount_total_signed = self.amount_total * sign
    #     # self.amount_untaxed_signed = amount_untaxed_signed * sign

    is_petty_cash = fields.Boolean(
        string='Petty Cash',
        readonly=True,
        states={'draft': [('readonly', False)]}, default=_get_is_petty_cash,
    )

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.with_context(ctx).write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv.date or inv.date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }

            if self.pfb_old_seq_dn_cn != '' and self.pfb_old_seq_dn_cn != False:
                move_vals.update({
                    'name': self.pfb_old_seq_dn_cn
                })
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            for line in move.line_ids:
                signed = 1
                vat_type = False
                if inv.type in ['out_refund', 'in_refund']:
                    signed = -1
                if inv.type in ['in_invoice','in_refund']:
                    vat_type = 'purchase'
                else:
                    vat_type = 'sale'
                if line.account_id.tax_sale_ok or line.account_id.tax_purchase_ok:
                    vat_obj = self.env['bione.account.vat']
                    new_data = {
                        'move_line_id': line.id,
                        'name': move.name,
                        'docdat': inv.date_invoice,
                        'vatprd': inv.date_invoice,
                        'partner_id': inv.partner_id.id,
                        'taxid': inv.partner_id.vat or '',
                        'depcod': '00000',
                        'amount_untaxed': inv.amount_untaxed_signed,
                        'amount_tax': inv.amount_tax * signed,
                        'amount_total': inv.amount_total_signed,
                        'invoice_id': inv.id,
                        'vat_type': vat_type,
                    }
                    vat = vat_obj.create(new_data)
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # if vat:
            #     vat.write({'name': move.name})
        return True

    @api.multi
    def action_invoice_open(self):
        if self.type in ('out_invoice'):
            params = self.env['ir.config_parameter'].sudo()
            for invoice in self:
                sql_check_single_tax = """
                 select distinct tax_id from account_invoice_line_tax ailt
                 join account_invoice_line ail on ail.id = ailt.invoice_line_id
                 where ail.invoice_id = %s
                 and tax_id is not null
                 """ % (invoice.id)
                self._cr.execute(sql_check_single_tax)
                taxes = self.env.cr.dictfetchall()
                if len(taxes) > 1:
                    raise UserError("ภาษีมีปัญหา! ใบกำกับใบนี้มีการกำหนดภาษีมากกว่า 1 ชนิด.")
                tax_id = False
                if taxes:
                    tax_id = taxes[0]['tax_id'] or False
                if tax_id:
                    tax_ids = []
                    for line in invoice.invoice_line_ids:
                        for des in self.deposit_ids:
                            unearned_income_account_id = int(
                                params.get_param('bione_thai_account.unearned_income_account_id', default=False)) or False,
                            tax_ids.append((4, tax_id, None))
                            line.create({
                                'invoice_id': invoice.id,
                                'name': des.name.name,
                                'account_id': unearned_income_account_id,
                                'price_unit': -des.amount_receipt,
                                'invoice_line_tax_ids': tax_ids,
                            })
                        invoice.compute_taxes()

        if self.type in ('in_invoice'):
            params = self.env['ir.config_parameter'].sudo()
            for invoice in self:
                sql_check_single_tax = """
                 select distinct tax_id from account_invoice_line_tax ailt
                 join account_invoice_line ail on ail.id = ailt.invoice_line_id
                 where ail.invoice_id = %s
                 and tax_id is not null
                 """ % (invoice.id)
                self._cr.execute(sql_check_single_tax)
                taxes = self.env.cr.dictfetchall()
                if len(taxes) > 1:
                    raise UserError("ภาษีมีปัญหา! ใบกำกับใบนี้มีการกำหนดภาษีมากกว่า 1 ชนิด.")
                tax_id = False
                if taxes:
                    tax_id = taxes[0]['tax_id'] or False
                if tax_id:
                    tax_ids = []
                    for line in invoice.invoice_line_ids:
                        for des in self.supplier_deposit_ids:
                            unearned_income_account_id = int(
                                params.get_param('bione_thai_account.unearned_expense_account_id', default=False)) or False,
                            tax_ids.append((4, tax_id, None))
                            line.create({
                                'invoice_id': invoice.id,
                                'name': des.name.name,
                                'account_id': unearned_income_account_id,
                                'price_unit': -des.amount_receipt,
                                'invoice_line_tax_ids': tax_ids,
                            })

        for invoice in self:
            sql_check_single_tax = """
             select distinct tax_id from account_invoice_line_tax ailt
             join account_invoice_line ail on ail.id = ailt.invoice_line_id
             where ail.invoice_id = %s
             and tax_id is not null
             """ % (invoice.id)
            self._cr.execute(sql_check_single_tax)
            taxes = self.env.cr.dictfetchall()
            if len(taxes) > 1:
                raise UserError("ภาษีมีปัญหา! ใบกำกับใบนี้มีการกำหนดภาษีมากกว่า 1 ชนิด.")
            tax_id = False
            if taxes:
                tax_id = taxes[0]['tax_id'] or False
            if tax_id:
                tax = self.env['account.tax'].browse(tax_id)
                if tax.price_include or tax.include_base_amount:
                    amount_untaxed = 0.0
                    amount_tax = 0.0
                    amount_total = 0.0
                    for line in invoice.invoice_line_ids:
                        amount_total += line.price_total
                    amount_tax = round(amount_total * 7 / 107, 2)
                    amount_untaxed = amount_total - amount_tax
                    diff_amount_untaxed = 0.0
                    diff_amount_tax = 0.0
                    if invoice.amount_untaxed != amount_untaxed:
                        diff_amount_untaxed = invoice.amount_untaxed - amount_untaxed
                    if invoice.amount_tax != amount_tax:
                        diff_amount_tax = invoice.amount_tax - amount_tax
                    sql_invoice = """
                                        update account_invoice
                                        set amount_untaxed = %s, amount_tax = %s, amount_total = %s, residual = %s
                                        where id = %s
                                    """ % (amount_untaxed, amount_tax, amount_total, amount_total, invoice.id)
                    self._cr.execute(sql_invoice)

                    sql_invoice_tax = """
                                    update account_invoice_tax
                                    set  amount = (select amount_tax from account_invoice where id = %s)
                                    where invoice_id = %s
                                                    """ % (invoice.id, invoice.id)
                    self._cr.execute(sql_invoice_tax)
                    if invoice.type in ('out_invoice','in_refund'):
                        sql_update_partner = """
                            update account_move_line
                            set debit = %s, amount_currency = %s
                            where account_id = (select account_id from account_invoice where id = %s)
                              and move_id = (select move_id from account_invoice where id = %s)
                        """ % (amount_total, amount_total, invoice.id, invoice.id )
                        self._cr.execute(sql_update_partner)
                        sql_update_tax = """
                            update account_move_line
                            set credit = %s
                            where account_id = (select account_id from account_tax where id = %s)
                              and move_id = (select move_id from account_invoice where id = %s)
                            """ % (amount_tax, tax.id, invoice.id)
                        self._cr.execute(sql_update_tax)
                        sql_update_product = """
                        update account_move_line
                            set credit = credit - %s
                            where id = 
                            (
                                select id from account_move_line
                                where move_id = (select move_id from account_invoice where id = %s)
                                  and account_id = (select account_id from account_invoice_line where invoice_id = %s limit 1) limit 1
                            )
                        """ % (round(diff_amount_untaxed,2), invoice.id, invoice.id)
                        self._cr.execute(sql_update_product)
                    elif invoice.type in ('in_invoice','out_refund'):
                        sql_update_partner = """
                            update account_move_line
                            set credit = %s, amount_currency = %s
                            where account_id = (select account_id from account_invoice where id = %s)
                              and move_id = (select move_id from account_invoice where id = %s)
                        """ % (amount_total, amount_total, invoice.id, invoice.id )
                        self._cr.execute(sql_update_partner)
                        sql_update_tax = """
                            update account_move_line
                            set debit = %s
                            where account_id = (select account_id from account_tax where id = %s)
                              and move_id = (select move_id from account_invoice where id = %s)
                            """ % (amount_tax, tax.id, invoice.id)
                        #print (sql_update_tax)
                        self._cr.execute(sql_update_tax)
                        sql_update_product = """
                        update account_move_line
                            set debit = debit - %s
                            where id = 
                            (
                                select id from account_move_line
                                where move_id = (select move_id from account_invoice where id = %s)
                                  and account_id = (select account_id from account_invoice_line where invoice_id = %s limit 1) limit 1
                            )
                        """ % (round(diff_amount_untaxed, 2), invoice.id, invoice.id)
                        self._cr.execute(sql_update_product)

        res = super(AccountInvoice, self).action_invoice_open()
        return res

    @api.multi
    def action_invoice_cancel(self):
        self.pfb_old_seq_dn_cn = self.number
        res = super(AccountInvoice, self).action_invoice_cancel()
        if self.type in ('out_invoice'):
            for invoice in self:
                for des in self.deposit_ids:
                    sql_line_ids = """
                                         DELETE FROM account_invoice_line
                                        where invoice_id  =  (select id from account_invoice where id  = %s)
                                        and name = '%s'
                                         """ % (invoice.id, des.name.name)
                    self._cr.execute(sql_line_ids)

                    sql_deposit_ids = """
                                         DELETE FROM bione_customer_payment_deposit
                                        where invoice_id  =  (select id from account_invoice where id  = %s)
                                         """ % (invoice.id)
                    self._cr.execute(sql_deposit_ids)

        if self.type in ('in_invoice'):
           for invoice_s in self:
                for des in self.supplier_deposit_ids:
                    ql_supplier_line_ids = """
                                        DELETE FROM account_invoice_line
                                       where invoice_id  =  (select id from account_invoice where id  = %s)
                                       and name = '%s'
                                       
                                        """ % (invoice_s.id,des.name.name)
                    self._cr.execute(ql_supplier_line_ids)

                    sql_supplier_deposit_ids = """
                                        DELETE FROM bione_supplier_payment_deposit
                                       where invoice_id  =  (select id from account_invoice where id  = %s)
                                        """ % (invoice_s.id)
                    self._cr.execute(sql_supplier_deposit_ids)
        return res

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            tax = tax_line.tax_id
            if tax.amount_type == "group":
                for child_tax in tax.children_tax_ids:
                    done_taxes.append(child_tax.id)
            res.append({
                'invoice_tax_line_id': tax_line.id,
                'tax_line_id': tax_line.tax_id.id,
                'type': 'tax',
                'name': tax_line.name,
                'price_unit': tax_line.amount_total,
                'quantity': 1,
                'price': tax_line.amount_total,
                'account_id': tax_line.account_id.id,
                'account_analytic_id': tax_line.account_analytic_id.id,
                'invoice_id': self.id,
                'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
            })
            done_taxes.append(tax.id)
        return res

    @api.onchange('cash_rounding_id', 'invoice_line_ids', 'tax_line_ids')
    def _onchange_cash_rounding(self):
        # Drop previous cash rounding lines
        lines_to_remove = self.invoice_line_ids.filtered(lambda l: l.is_rounding_line)
        if lines_to_remove:
            self.invoice_line_ids -= lines_to_remove

        # Clear previous rounded amounts
        #for tax_line in self.tax_line_ids:
        #    if tax_line.amount_rounding != 0.0:
        #        tax_line.amount_rounding = 0.0

        if self.cash_rounding_id and self.type in ('out_invoice', 'out_refund'):
            rounding_amount = self.cash_rounding_id.compute_difference(self.currency_id, self.amount_total)
            if not self.currency_id.is_zero(rounding_amount):
                if self.cash_rounding_id.strategy == 'biggest_tax':
                    # Search for the biggest tax line and add the rounding amount to it.
                    # If no tax found, an error will be raised by the _check_cash_rounding method.
                    if not self.tax_line_ids:
                        return
                    biggest_tax_line = None
                    for tax_line in self.tax_line_ids:
                        if not biggest_tax_line or tax_line.amount > biggest_tax_line.amount:
                            biggest_tax_line = tax_line
                    #biggest_tax_line.amount_rounding += rounding_amount
                elif self.cash_rounding_id.strategy == 'add_invoice_line':
                    # Create a new invoice line to perform the rounding
                    rounding_line = self.env['account.invoice.line'].new({
                        'name': self.cash_rounding_id.name,
                        'invoice_id': self.id,
                        'account_id': self.cash_rounding_id.account_id.id,
                        'price_unit': rounding_amount,
                        'quantity': 1,
                        'is_rounding_line': True,
                        'sequence': 9999  # always last line
                    })

                    # To be able to call this onchange manually from the tests,
                    # ensure the inverse field is updated on account.invoice.
                    if not rounding_line in self.invoice_line_ids:
                        self.invoice_line_ids += rounding_line

    @api.multi
    def action_clear(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        price_unit = 0.00
        self.amount_tax = 0.0
        self.amount_total = self.amount_untaxed
        self.amount_total_signed = self.amount_total
        for rec in self.invoice_line_ids:
            if rec.invoice_line_tax_ids.name == 'ภาษีซื้อ ไม่รวม VAT':
                price_unit = (rec.price_unit * 7 / 100) + rec.price_unit
                print(price_unit)
                rec.write({'price_unit': price_unit})
            if rec.invoice_line_tax_ids:
                rec.invoice_line_tax_ids = False
        self.tax_line_ids = False

    def name_get(self):
        # ให้ทำงานเฉพาะหน้ารับชำระ จ่ายชำระ เท่านั้น
        if self._context.get('payment_view',False) != True:
            return super(AccountInvoice, self).name_get()
        result = []
        for invoice in self:
            name = invoice.number
            if invoice.date_invoice:
                result.append((invoice.id, _("%(name)s | %(date)s | %(amount)s") % {
                    'name': name,
                    'date': fields.Date.from_string(invoice.date_invoice).strftime("%d/%m/%Y"),
                    'amount': '{:,.2f}'.format(invoice.amount_total),
                }))

        return result

    @api.multi
    @api.constrains('invoice_line_ids')
    def _check_petty_cash_amount(self):
        petty_cash_env = self.env['account.petty.fund']
        for rec in self.filtered('is_petty_cash'):
            petty_cash = petty_cash_env.search(
                [('partner_id', '=', rec.partner_id.id)], limit=1)
            if not petty_cash:
                raise ValidationError(_('%s is not a petty cash holder') %
                                      rec.partner_id.name)
            balance = petty_cash.balance
            limit = petty_cash.max_amount
            max_amount = limit - balance
            account = petty_cash.account_id
            amount = sum(rec.invoice_line_ids.filtered(
                lambda l: l.account_id == account).mapped('price_subtotal'))
            company_currency = rec.company_id.currency_id
            amount_company = rec.currency_id._convert(
                amount, company_currency, rec.company_id,
                rec.date_invoice or fields.Date.today())
            if amount_company > max_amount:
                raise ValidationError(
                    _('Petty Cash balance is %s %s.\n'
                      'Max amount to add is %s %s.') %
                    ('{:,.2f}'.format(balance), company_currency.symbol,
                     '{:,.2f}'.format(max_amount), company_currency.symbol))

    @api.multi
    def _add_petty_cash_invoice_line(self, petty_cash):
        self.ensure_one()
        # Get suggested currency amount
        amount = petty_cash.max_amount - petty_cash.balance
        company_currency = self.env.user.company_id.currency_id
        amount_doc_currency = company_currency._convert(
            amount, self.currency_id, self.company_id,
            self.date_invoice or fields.Date.today())
        # print(petty_cash)

        params = self.env['ir.config_parameter'].sudo()
        self.journal_id = int(params.get_param('bione_thai_account.petty_cash_receipt_journal_id', default=False)) or False

        inv_line = self.env['account.invoice.line'].new({
            'name': petty_cash.account_id.name,
            'invoice_id': self.id,
            'account_id': petty_cash.account_id.id,
            'price_unit': amount_doc_currency,
            'quantity': 1,
        })
        # print(inv_line)
        return inv_line

    @api.multi
    @api.onchange('is_petty_cash', 'partner_id')
    def _onchange_is_petty_cash(self):
        self.invoice_line_ids = False
        if self.is_petty_cash:
            # Selected parenter must be petty cash holder
            petty_cash = self.env['account.petty.fund'].search(
                [('partner_id', '=', self.partner_id.id)], limit=1)
            # print(petty_cash)
            if not petty_cash:
                raise ValidationError(_('%s is not a petty cash holder') %
                                      self.partner_id.name)
            self._add_petty_cash_invoice_line(petty_cash)