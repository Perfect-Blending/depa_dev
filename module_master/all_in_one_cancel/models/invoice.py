from odoo import api, fields, models,exceptions


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cancel_paid_invoice = fields.Boolean(string='Cancel Paid Invoice?', compute='check_cancel_paid_invoice')

    @api.model
    def check_cancel_paid_invoice(self):

        for invoice in self:
            if invoice.company_id.cancel_paid_invoice:
                invoice.cancel_paid_invoice = True

    @api.multi
    def action_cancel(self):
        for invoice in self:
            if invoice.company_id.cancel_paid_invoice:
                if invoice.journal_id and not invoice.journal_id.update_posted:
                    invoice.journal_id.write({'update_posted':True})
                    # invoice.number = invoice.move_name
                    # invoice
                    moves = invoice.move_id
                    if moves and not moves.journal_id.update_posted:
                        moves.write({'update_posted':True})
        res = super(AccountInvoice,self).action_cancel()
        return res
