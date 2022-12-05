from odoo import models, fields, api, _


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_clear(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        self.amount_tax = 0.0
        self.amount_total = self.amount_untaxed
        self.amount_total_signed = self.amount_total
        for rec in self.invoice_line_ids:
            if rec.invoice_line_tax_ids:
                rec.invoice_line_tax_ids = False
        self.tax_line_ids = False
