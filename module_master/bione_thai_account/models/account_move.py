# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class AccountMove(models.Model):

    _inherit = "account.move"
    _order = 'date desc,name desc'

    payment_ids = fields.One2many('bione.customer.payment', 'move_id', string=u'รับชำระ')
    deposit_ids = fields.One2many('bione.customer.deposit', 'move_id', string=u'รับมัดจำ')
    vat_ids = fields.One2many('bione.account.vat', 'move_line_id', string=u'ภาษีซื้อ')
    wht_ids = fields.One2many('bione.wht', 'move_line_id', string=u'ภาษีหัก ณ ที่จ่าย')
    note = fields.Text(
        string="Note",
        required=False)

    @api.multi
    def _post_validate(self):
        res = super(AccountMove, self)._post_validate()
        for move in self:
            if move.line_ids:
                for line in move.line_ids:
                    if line.tax_ok:
                        total_vat = max(line.debit, line.credit)
                        check_vat = 0.0
                        if not (line.move_id.payment_ids or line.move_id.deposit_ids) and line.vat_ids:
                            for vat in line.vat_ids:
                                check_vat += abs(vat.amount_tax)
                            if round(total_vat, 2) != round(check_vat, 2):
                                raise UserError(u'ยอดภาษีไม่ตรง หรือยังคีย์ไม่ครบ')
                    if line.wht_ok:
                        total_wht = max(line.debit, line.credit)
                        check_wht = 0.0
                        if not (line.move_id.payment_ids or line.move_id.deposit_ids) and line.wht_ids:
                            for vat in line.wht_ids:
                                check_wht += vat.tax
                            if round(total_wht, 2) != round(check_wht, 2):
                                raise UserError(u'ยอดภาษีหัก ณ ที่จ่ายไม่ตรง หรือยังคีย์ไม่ครบ')
                    if line.cheque_ids:
                        total_cheque = max(line.debit, line.credit)
                        check_cheque = 0.0
                        if not line.move_id.payment_ids or line.move_id.deposit_ids:
                            for vat in line.cheque_ids:
                                check_cheque += vat.amount
                            if total_cheque != check_cheque:
                                raise UserError(u'ยอดเช็คไม่ตรง หรือยังคีย์ไม่ครบ')
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.one
    @api.depends('account_id')
    def _get_tax(self):
        self.tax_ok = self.account_id.tax_sale_ok or self.account_id.tax_purchase_ok or False

    @api.one
    @api.depends('account_id')
    def _get_cheque(self):
        self.cheque_ok = self.account_id.cheque_in_ok or self.account_id.cheque_out_ok or False

    @api.one
    @api.depends('account_id')
    def _get_wht(self):
        self.wht_ok = self.account_id.wht_sale_ok or self.account_id.wht_purchase_ok or False
        self.wht_sale_ok = self.account_id.wht_sale_ok or False
        self.wht_purchase_ok = self.account_id.wht_purchase_ok or False

    @api.one
    @api.depends('account_id')
    def _get_account_type(self):
        self.receivable_ok = self.account_id.user_type_id.type == 'receivable' or False
        self.payable_ok = self.account_id.user_type_id.type == 'payable' or False

    #inherit
    @api.one
    @api.depends('move_id')
    def _compute_parent_state(self):
        self.parent_state = self.move_id.state

    # inherit (replace old method)
    @api.model
    def default_get(self, fields):
        rec = {}
        if 'line_ids' not in self._context:
            return rec
        balance = 0
        for line in self._context['line_ids']:
            if line[2]:
                balance += line[2].get('debit', 0.0) - line[2].get('credit', 0.0)
        if balance < 0:
            rec.update({'debit': -balance})
        if balance > 0:
            rec.update({'credit': balance})
        return rec

    vat_ids = fields.One2many('bione.account.vat', 'move_line_id', string='Vat')
    wht_ids = fields.One2many('bione.wht', 'move_line_id', string='With Holding Tax')
    cheque_ids = fields.One2many('bione.cheque', 'move_line_id', string='Cheques')
    tax_ok = fields.Boolean(string='Tax Ok', compute='_get_tax', readonly=True)
    wht_ok = fields.Boolean(string='WHT Ok', compute='_get_wht', readonly=True)
    wht_sale_ok = fields.Boolean(string='WHT Sale Ok', compute='_get_wht', readonly=True)
    wht_purchase_ok = fields.Boolean(string='WHT Purchase Ok', compute='_get_wht', readonly=True)
    receivable_ok = fields.Boolean(string='Receivable Ok', compute='_get_account_type', readonly=True)
    payable_ok = fields.Boolean(string='Payable Ok', compute='_get_account_type', readonly=True)
    cheque_ok = fields.Boolean(string='Cheque Ok', compute='_get_cheque', readonly=True)
    date_maturity = fields.Date(string='Due date', index=True, required=False,
        help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")

