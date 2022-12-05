from odoo import models, fields, api, _


class PurchaseInvoicePlanInherit(models.Model):
    _inherit = 'purchase.invoice.plan'

    amount_invoice_plan = fields.Float(string='Amount', digits=(12, 2))
    percent = fields.Float(
        string='Percent',
        digits=(12, 2),
        help="This percent will be used to calculate new quantity"
    )
    percent_all = fields.Char(digits=(12, 2))
    amount_all = fields.Char(digits=(12, 2))

    @api.onchange('percent')
    def set_amount(self):
        for rec in self:
            if rec.percent:
                sum_amount = rec.purchase_id.amount_total
                percent = rec.percent
                rec.amount_invoice_plan = (percent * sum_amount) / 100
                print(rec.amount_invoice_plan, sum_amount)

    @api.onchange('amount_invoice_plan')
    def set_amount2(self):
        for rec in self:
            if rec.amount_invoice_plan:
                sum_amount = rec.purchase_id.amount_total
                rec.percent = (100 / sum_amount) * self.amount_invoice_plan
                print(rec.percent)

    @api.multi
    def _compute_new_invoice_quantity(self, invoice):
        return True
