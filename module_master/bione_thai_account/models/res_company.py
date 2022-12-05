# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"
    # _order = "sequence, code"

    # code = fields.Char("Code")
    # fax = fields.Char(string='Fax')
    # cheque_postdate_in_account_id = fields.Many2one('account.account', string='Post Date Cheque(Receive)',
    #                                                 domain=[('deprecated', '=', False)], index=True)
    # out_cheque_journal_id = fields.Many2one('account.journal', string='Cheque Payment', index=True,
    #                                         help="Journal for Cheque Payment")
    # in_cheque_journal_id = fields.Many2one('account.journal', string='Cheque Receipt', index=True,
    #                                        help="Journal for Cheque Receive")
    #
    # credit_card_postdate_in_account_id = fields.Many2one('account.account', string='Post Date Credit Card(Receive)',
    #                                                      domain=[('deprecated', '=', False)], index=True, )
    # out_credit_card_journal_id = fields.Many2one('account.journal', string='Credit Card Payment', index=True,
    #                                              help="Journal for Credit Card Payment")
    # in_credit_card_journal_id = fields.Many2one('account.journal', string='Credit Card Receipt', index=True,
    #                                             help="Journal for Credit Card Receive")
    #
    # # bank_journal_id = fields.Many2one('account.journal', string='Bank', index=True,
    # #                                   help="Journal for Bank")
    #
    # cash_account_id = fields.Many2one('account.account', string='Cash', domain=[('deprecated', '=', False)],
    #                                   index=True, )
    # # bank_charge_account_id = fields.Many2one('account.account', string='Bank Charge Account',
    # #                                          domain=[('deprecated', '=', False)], index=True,
    # #                                          help="Bank Charge Account")
    # bank_income_account_id = fields.Many2one('account.account', string='Bank Income Account',
    #                                          domain=[('deprecated', '=', False)], index=True,
    #                                          help="Bank Income Account")
    # bank_book_account_id = fields.Many2one('account.account', string='Bank Book Account',
    #                                        domain=[('deprecated', '=', False)], index=True,
    #                                        help="Bank Book Account")
    # advance_account_id = fields.Many2one('account.account', string='Advance Account',
    #                                      domain=[('deprecated', '=', False)], index=True, )
    # bank_write_off_account_id = fields.Many2one('account.account', string='Write-off Account',
    #                                             domain=[('deprecated', '=', False)], index=True, )
    # wht_company_account_id = fields.Many2one('account.account', string='WHT Company Account',
    #                                          domain=[('deprecated', '=', False)], index=True, )
    # wht_personal_account_id = fields.Many2one('account.account', string='WHT Personal Account',
    #                                           domain=[('deprecated', '=', False)], index=True, )
    # pp30_account_id = fields.Many2one('account.account', string='PP30 Account', domain=[('deprecated', '=', False)],
    #                                   index=True, )
    # pp40_account_id = fields.Many2one('account.account', string='PP40 Personal Account',
    #                                   domain=[('deprecated', '=', False)], index=True, )
    # pnd2_account_id = fields.Many2one('account.account', string='PND2 Personal Account',
    #                                   domain=[('deprecated', '=', False)], index=True, )
    # cheque_postdate_out_account_id = fields.Many2one('account.account', string='Post Date Cheque (Payment)',
    #                                                  domain=[('deprecated', '=', False)], index=True, )
    # credit_card_postdate_out_account_id = fields.Many2one('account.account', string='Post Date Credit Card (Payment)',
    #                                                       domain=[('deprecated', '=', False)], index=True, )
    #
    # # journal
    # # vendor_bill_journal_id = fields.Many2one('account.journal', string='Vendor Bill', index=True, )
    # vendor_credit_note_journal_id = fields.Many2one('account.journal', string='Vendor Credit Note', index=True, )
    # vendor_debit_note_journal_id = fields.Many2one('account.journal', string='Vendor Debit Note', index=True, )
    # vendor_deposit_journal_id = fields.Many2one('account.journal', string='Vendor Deposit', index=True, )
    # vendor_cash_journal_id = fields.Many2one('account.journal', string='Vendor Cash', index=True, )
    #
    # customer_invoice_journal_id = fields.Many2one('account.journal', string='Customer Invoice', index=True, )
    # customer_credit_note_journal_id = fields.Many2one('account.journal', string='Customer Credit Note', index=True, )
    # customer_debit_note_journal_id = fields.Many2one('account.journal', string='Customer Debit Note', index=True, )
    # customer_deposit_journal_id = fields.Many2one('account.journal', string='Customer Deposit', index=True, )
    # customer_cash_journal_id = fields.Many2one('account.journal', string='Customer Cash', index=True, )
    #
    # receipt_journal_id = fields.Many2one('account.journal', string='Receipt', index=True, )
    # # payment_journal_id = fields.Many2one('account.journal', string='Payment', index=True, )
    # advance_journal_id = fields.Many2one('account.journal', string='Advance', index=True, )
    # petty_cash_receipt_journal_id = fields.Many2one('account.journal', string='Petty Cash Receipt', index=True, )
    # petty_cash_payment_journal_id = fields.Many2one('account.journal', string='Petty Cash Payment', index=True, )
    # depr_asset_journal_id = fields.Many2one('account.journal', string='Depr Asset Payment', index=True, )
    # cash_deposit_journal_id = fields.Many2one('account.journal', string='Cash Deposit', index=True, )
    # cash_withdraw_journal_id = fields.Many2one('account.journal', string='Cash Withdraw', index=True, )
    # bank_transfer_journal_id = fields.Many2one('account.journal', string='Bank Transfer', index=True, )
    # bank_charge_journal_id = fields.Many2one('account.journal', string='Bank Charge', index=True, )
    # bank_income_journal_id = fields.Many2one('account.journal', string='Bank Income', index=True, )
    # journal_id = fields.Many2one('account.journal', string='Journal Entry', index=True, )

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for company in self:
    #         name = company.name
    #         if company.code:
    #             name = '[' + company.code + '] ' + name
    #         res.append((company.id, name))
    #     return res
