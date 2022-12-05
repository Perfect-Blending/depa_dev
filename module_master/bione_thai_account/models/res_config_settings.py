# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cash_account_id = fields.Many2one('account.account', string=u'เงินสด', required=True)
    #Account Receivable
    interest_income_account_id = fields.Many2one('account.account', string=u'ดอกเบี้ยรับ', required=True)
    cash_discount_account_id = fields.Many2one('account.account', string=u'ส่วนลดเงินสด', required=True)
    wht_sale_account_id = fields.Many2one('account.account', string=u'ภาษีถูกหัก ณ ที่จ่าย', required=True)
    cheque_sale_account_id = fields.Many2one('account.account', string=u'เช็ครับ', required=True)
    vat_sale_account_id = fields.Many2one('account.account', string=u'ภาษีขาย', required=True)
    unearned_income_account_id = fields.Many2one('account.account', string=u'รายได้รับล่วงหน้า', required=True)
    undue_sale_tax_account_id = fields.Many2one('account.account', string=u'ภาษีขาย-รอเรียกเก็บ', required=True)
    revenue_income_account_id = fields.Many2one('account.account', string=u'รายได้ขายสด', required=True)
    #Account Payable
    interest_expense_account_id = fields.Many2one('account.account', string=u'ดอกเบี้ยจ่าย', required=True)
    cash_income_account_id = fields.Many2one('account.account', string=u'ส่วนลดรับ', required=True)
    wht_purchase_account_id = fields.Many2one('account.account', string=u'ภาษีหัก ณ ที่จ่าย', required=True)

    wht_purchase1_account_id = fields.Many2one('account.account', string=u'ภาษีหัก ณ ที่จ่าย 1', required=True)
    wht_purchase2_account_id = fields.Many2one('account.account', string=u'ภาษีหัก ณ ที่จ่าย 2', required=True)
    wht_purchase3_account_id = fields.Many2one('account.account', string=u'ภาษีหัก ณ ที่จ่าย 3', required=True)
    wht_purchase53_account_id = fields.Many2one('account.account', string=u'ภาษีหัก ณ ที่จ่าย 53', required=True)

    cheque_purchase_account_id = fields.Many2one('account.account', string=u'เช็คจ่าย', required=True)
    vat_purchase_account_id = fields.Many2one('account.account', string=u'ภาษีซื้อ', required=True)
    unearned_expense_account_id = fields.Many2one('account.account', string=u'รายจ่ายล่วงหน้า', required=True)
    undue_purchase_tax_account_id = fields.Many2one('account.account', string=u'ภาษีซื้อ-ยังไม่ถึงกำหนด', required=True)
    advance_account_id = fields.Many2one('account.account', string='Advance Account', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal Entry', index=True, required=True)
    petty_cash_payment_journal_id = fields.Many2one('account.journal', string='Petty Cash Payment', index=True, required=True)
    petty_cash_receipt_journal_id = fields.Many2one('account.journal', string='Petty Cash Receipt', index=True, required=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            cash_account_id=int(params.get_param('bione_thai_account.cash_account_id', default=False)) or False,
            # Account Receivable
            interest_income_account_id=int(params.get_param('bione_thai_account.interest_income_account_id', default=False)) or False,
            cash_discount_account_id=int(params.get_param('bione_thai_account.cash_discount_account_id', default=False)) or False,
            wht_sale_account_id=int(params.get_param('bione_thai_account.wht_sale_account_id', default=False)) or False,
            cheque_sale_account_id=int(params.get_param('bione_thai_account.cheque_sale_account_id', default=False)) or False,
            vat_sale_account_id=int(params.get_param('bione_thai_account.vat_sale_account_id', default=False)) or False,
            unearned_income_account_id=int(params.get_param('bione_thai_account.unearned_income_account_id', default=False)) or False,
            undue_sale_tax_account_id=int(
                params.get_param('bione_thai_account.undue_sale_tax_account_id', default=False)) or False,
            revenue_income_account_id=int(
                params.get_param('bione_thai_account.revenue_income_account_id', default=False)) or False,

            #Account Payable
            interest_expense_account_id=int(
                params.get_param('bione_thai_account.interest_expense_account_id', default=False)) or False,
            cash_income_account_id=int(
                params.get_param('bione_thai_account.cash_income_account_id', default=False)) or False,

            wht_purchase_account_id=int(params.get_param('bione_thai_account.wht_purchase_account_id', default=False)) or False,

            wht_purchase1_account_id=int(
                params.get_param('bione_thai_account.wht_purchase1_account_id', default=False)) or False,
            wht_purchase2_account_id=int(
                params.get_param('bione_thai_account.wht_purchase2_account_id', default=False)) or False,
            wht_purchase3_account_id=int(
                params.get_param('bione_thai_account.wht_purchase3_account_id', default=False)) or False,
            wht_purchase53_account_id=int(
                params.get_param('bione_thai_account.wht_purchase53_account_id', default=False)) or False,

            cheque_purchase_account_id=int(
                params.get_param('bione_thai_account.cheque_purchase_account_id', default=False)) or False,
            vat_purchase_account_id=int(params.get_param('bione_thai_account.vat_purchase_account_id', default=False)) or False,
            unearned_expense_account_id=int(
                params.get_param('bione_thai_account.unearned_expense_account_id', default=False)) or False,
            undue_purchase_tax_account_id=int(
                params.get_param('bione_thai_account.undue_purchase_tax_account_id', default=False)) or False,
            advance_account_id=int(
                params.get_param('bione_thai_account.advance_account_id', default=False)) or False,
            journal_id=int(
                params.get_param('bione_thai_account.journal_id', default=False)) or False,
            petty_cash_payment_journal_id=int(
                params.get_param('bione_thai_account.petty_cash_payment_journal_id', default=False)) or False,
            petty_cash_receipt_journal_id=int(
                params.get_param('bione_thai_account.petty_cash_receipt_journal_id', default=False)) or False,

        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.cash_account_id", self.cash_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.interest_income_account_id", self.interest_income_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.cash_discount_account_id", self.cash_discount_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.wht_sale_account_id", self.wht_sale_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.cheque_sale_account_id", self.cheque_sale_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.vat_sale_account_id", self.vat_sale_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.unearned_income_account_id", self.unearned_income_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.undue_sale_tax_account_id", self.undue_sale_tax_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.revenue_income_account_id", self.revenue_income_account_id.id or False)
        # Account Payable
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.interest_expense_account_id", self.interest_expense_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.cash_income_account_id", self.cash_income_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.wht_purchase_account_id", self.wht_purchase_account_id.id or False)

        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.wht_purchase1_account_id", self.wht_purchase1_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.wht_purchase2_account_id", self.wht_purchase2_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.wht_purchase3_account_id", self.wht_purchase3_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.wht_purchase53_account_id", self.wht_purchase53_account_id.id or False)

        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.cheque_purchase_account_id", self.cheque_purchase_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.vat_purchase_account_id", self.vat_purchase_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.unearned_expense_account_id", self.unearned_expense_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.undue_purchase_tax_account_id", self.undue_purchase_tax_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.advance_account_id", self.advance_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.journal_id", self.journal_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.petty_cash_payment_journal_id", self.petty_cash_payment_journal_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("bione_thai_account.petty_cash_receipt_journal_id", self.petty_cash_receipt_journal_id.id or False)



