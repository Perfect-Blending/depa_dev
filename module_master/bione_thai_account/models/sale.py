# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    deposit_ids = fields.One2many('bione.customer.deposit', 'sale_order_id', string='Deposits')

    @api.multi
    def action_view_deposit(self):
        deposits = self.mapped('deposit_ids')
        action = self.env.ref('bione_thai_account.action_bione_customer_deposit').read()[0]
        if len(deposits) > 1:
            action['domain'] = [('id', 'in', deposits.ids)]
        elif len(deposits) == 1:
            action['views'] = [(self.env.ref('bione_thai_account.view_bione_customer_deposit_form').id, 'form')]
            action['res_id'] = deposits.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
