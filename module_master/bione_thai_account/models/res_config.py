# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"

    cheque_postdate_in_account_id = fields.Many2one('account.account', string='Post Date Cheque (Receive)',
        related='company_id.cheque_postdate_in_account_id')
    cheque_postdate_out_account_id = fields.Many2one('account.account', string='Post Date Cheque (Payment)',
        related='company_id.cheque_postdate_out_account_id')
    bank_charge_account_id = fields.Many2one('account.account', string='Bank Charge Account',
        related='company_id.bank_charge_account_id')
    credit_card_postdate_in_account_id = fields.Many2one('account.account', string='Post Date Credit Card (Receive)',
        related='company_id.credit_card_postdate_in_account_id')
    credit_card_postdate_out_account_id = fields.Many2one('account.account', string='Post Date Credit Card (Payment)',
        related='company_id.credit_card_postdate_out_account_id')
    cash_account_id = fields.Many2one('account.account', string='Cash',
        related='company_id.cash_account_id')
    bank_income_account_id = fields.Many2one('account.account', string='Bank Income',
        related='company_id.bank_income_account_id')
    bank_book_account_id = fields.Many2one('account.account', string='Bank Book Company',
        related='company_id.bank_book_account_id')
    advance_account_id = fields.Many2one('account.account', string='Advance Account', related='company_id.advance_account_id')
    bank_write_off_account_id = fields.Many2one('account.account', string='Write-off Account', related='company_id.bank_write_off_account_id')
    wht_company_account_id = fields.Many2one('account.account', string='WHT Company Account', related='company_id.wht_company_account_id')
    wht_personal_account_id = fields.Many2one('account.account', string='WHT Personal Account', related='company_id.wht_personal_account_id')
    pp30_account_id = fields.Many2one('account.account', string='PP30 Account', related='company_id.pp30_account_id')
    pp40_account_id = fields.Many2one('account.account', string='PP40 Personal Account', related='company_id.pp40_account_id')
    pnd2_account_id = fields.Many2one('account.account', string='PND2 Personal Account', related='company_id.pnd2_account_id')

    #journal
    vendor_bill_journal_id = fields.Many2one('account.journal', string='Vendor Bill', related='company_id.vendor_bill_journal_id')
    vendor_credit_note_journal_id = fields.Many2one('account.journal', string='Vendor Credit Note', related='company_id.vendor_credit_note_journal_id')
    vendor_debit_note_journal_id = fields.Many2one('account.journal', string='Vendor Debit Note', related='company_id.vendor_debit_note_journal_id')
    vendor_deposit_journal_id = fields.Many2one('account.journal', string='Vendor Deposit', related='company_id.vendor_deposit_journal_id')

    vendor_cash_journal_id = fields.Many2one('account.journal', string='Vendor cash', related='company_id.vendor_cash_journal_id')

    customer_invoice_journal_id = fields.Many2one('account.journal', string='Customer Invoice', related='company_id.customer_invoice_journal_id')
    customer_credit_note_journal_id = fields.Many2one('account.journal', string='Customer Credit Note', related='company_id.customer_credit_note_journal_id')
    customer_debit_note_journal_id = fields.Many2one('account.journal', string='Customer Debit Note', related='company_id.customer_debit_note_journal_id')
    customer_deposit_journal_id = fields.Many2one('account.journal', string='Customer Deposit', related='company_id.customer_deposit_journal_id')
    customer_cash_journal_id = fields.Many2one('account.journal', string='Customer Cash', related='company_id.customer_cash_journal_id')

    receipt_journal_id = fields.Many2one('account.journal', string='Receipt', related='company_id.receipt_journal_id')
    payment_journal_id = fields.Many2one('account.journal', string='Payment', related='company_id.payment_journal_id')

    out_cheque_journal_id = fields.Many2one('account.journal', string='Cheque Payment',
        related='company_id.out_cheque_journal_id',
        help="Journal for Cheque Payment")
    in_cheque_journal_id = fields.Many2one('account.journal', string='Cheque Receipt',
        related='company_id.in_cheque_journal_id',
        help="Journal for Cheque Receive")
    out_credit_card_journal_id = fields.Many2one('account.journal', string='Credit Card Payment',
        related='company_id.out_credit_card_journal_id',
        help="Journal for Credit Card Payment")
    in_credit_card_journal_id = fields.Many2one('account.journal', string='Credit Card Receipt',
        related='company_id.in_credit_card_journal_id',
        help="Journal for Credit Card Receive")
    bank_journal_id = fields.Many2one('account.journal', string='Bank',
        related='company_id.bank_journal_id',
        help="Journal for Bank")

    advance_journal_id  = fields.Many2one('account.journal', string='Advance', related='company_id.advance_journal_id')
    petty_cash_receipt_journal_id  = fields.Many2one('account.journal', string='Petty Cash Receipt', related='company_id.petty_cash_receipt_journal_id')
    petty_cash_payment_journal_id  = fields.Many2one('account.journal', string='Petty Cash Payment', related='company_id.petty_cash_payment_journal_id')
    depr_asset_journal_id  = fields.Many2one('account.journal', string='Depr Asset Payment', related='company_id.depr_asset_journal_id')
    cash_deposit_journal_id  = fields.Many2one('account.journal', string='Cash Deposit', related='company_id.cash_deposit_journal_id')
    cash_withdraw_journal_id  = fields.Many2one('account.journal', string='Cash Withdraw', related='company_id.cash_withdraw_journal_id')
    bank_transfer_journal_id  = fields.Many2one('account.journal', string='Bank Transfer', related='company_id.bank_transfer_journal_id')
    bank_charge_journal_id  = fields.Many2one('account.journal', string='Bank Charge', related='company_id.bank_charge_journal_id')
    bank_income_journal_id  = fields.Many2one('account.journal', string='Bank Income', related='company_id.bank_income_journal_id')
    journal_id  = fields.Many2one('account.journal', string='Journal Entry', related='company_id.journal_id')

    group_journal_id = fields.Boolean(string='Group Journal Entry')
    auto_post_journal_id = fields.Boolean(string='Auto Post Journal Entry')

    @api.multi
    def set_cheque_postdate_in_account(self):
        if self.cheque_postdate_in_account_id and self.cheque_postdate_in_account_id != self.company_id.cheque_postdate_in_account_id:
            self.company_id.write({'cheque_postdate_in_account_id': self.cheque_postdate_in_account_id.id})

    @api.multi
    def set_credit_card_postdate_in_account(self):
        if self.credit_card_postdate_in_account_id and self.credit_card_postdate_in_account_id != self.company_id.credit_card_postdate_in_account_id:
            self.company_id.write({'credit_card_postdate_in_account_id': self.credit_card_postdate_in_account_id.id})

    @api.multi
    def set_bank_charge_account_id(self):
        if self.bank_charge_account_id and self.bank_charge_account_id != self.company_id.bank_charge_account_id:
            self.company_id.write({'bank_charge_account_id': self.bank_charge_account_id.id})

    @api.multi
    def set_bank_income_account_id(self):
        if self.bank_income_account_id and self.bank_income_account_id != self.company_id.bank_income_account_id:
            self.company_id.write({'bank_income_account_id': self.bank_income_account_id.id})

    @api.multi
    def set_cash_account_id(self):
        if self.cash_account_id and self.cash_account_id != self.company_id.cash_account_id:
            self.company_id.write({'cash_account_id': self.cash_account_id.id})


    # ***********************************************************

    @api.multi
    def set_out_cheque_journal_id(self):
        if self.out_cheque_journal_id and self.out_cheque_journal_id != self.company_id.out_cheque_journal_id:
            self.company_id.write({'out_cheque_journal_id': self.out_cheque_journal_id.id})

    @api.multi
    def set_in_cheque_journal_id(self):
        if self.in_cheque_journal_id and self.in_cheque_journal_id != self.company_id.in_cheque_journal_id:
            self.company_id.write({'in_cheque_journal_id': self.in_cheque_journal_id.id})

    @api.multi
    def set_out_credit_card_journal_id(self):
        if self.out_credit_card_journal_id and self.out_credit_card_journal_id != self.company_id.out_credit_card_journal_id:
            self.company_id.write({'out_credit_card_journal_id': self.out_credit_card_journal_id.id})

    @api.multi
    def set_in_credit_card_journal_id(self):
        if self.in_credit_card_journal_id and self.in_credit_card_journal_id != self.company_id.in_credit_card_journal_id:
            self.company_id.write({'in_credit_card_journal_id': self.in_credit_card_journal_id.id})

    @api.multi
    def set_bank_journal_id(self):
        if self.bank_journal_id and self.bank_journal_id != self.company_id.bank_journal_id:
            self.company_id.write({'bank_journal_id': self.bank_journal_id.id})
