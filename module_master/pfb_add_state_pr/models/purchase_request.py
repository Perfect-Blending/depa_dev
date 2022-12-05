from odoo import models, fields, api, _


class AccountInvoiceInherit(models.Model):
    _inherit = 'purchase.request'

    state = fields.Selection(selection_add=[('submitted', 'Submitted')])

    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted'),
                              ('to_approve', 'To be approved'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('done', 'Done')],
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')

    @api.multi
    def button_sen(self):
        self.write({'state': 'submitted'})
        return {}

    def button_approved2(self):
        self.write({'state': 'approved'})
        return {}
