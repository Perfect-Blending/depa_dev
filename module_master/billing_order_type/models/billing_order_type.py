# Copyright (C) 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BillingOrderType(models.Model):
    _name = 'billing.order.type'
    _description = 'Type of Billing order'
    _order = 'sequence'

    @api.model
    def _get_domain_sequence_id(self):
        # seq_type = self.env.ref('account.sequence_payment_supplier_invoice')
        seq_type = self.env.ref('account_billing.seq_account_customer_billing')
        return [('code', '=', seq_type.code)]

    @api.model
    def _default_sequence_id(self):
        seq_type = self.env.ref('account_billing.seq_account_customer_billing')
        return seq_type.id

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description', translate=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Entry Sequence', copy=False,
        domain=_get_domain_sequence_id, default=_default_sequence_id,
        required=True)
    # payment_term_id = fields.Many2one(
    #     comodel_name='account.payment.term', string='Payment Terms')
    # incoterm_id = fields.Many2one(
    #     comodel_name='account.incoterms', string='Incoterm')
    sequence = fields.Integer(default=10)
