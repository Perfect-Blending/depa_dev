from odoo import fields, models, api
import datetime


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    vatprd = fields.Date(string='วันที่ยื่น')
    vat_period = fields.Char(string='งวดที่')

    @api.onchange('tax_date_manual')
    def change_docdat(self):
        self.vatprd = self.tax_date_manual

    @api.onchange('vatprd')
    def change_vat_date(self):
        self.vat_period = self.calc_vat_date(self.vatprd)

    def calc_vat_date(self, vatprd):
        if vatprd:
            dtdt = (self.vatprd).strftime('%Y-%m')
            return dtdt
        else:
            return False
