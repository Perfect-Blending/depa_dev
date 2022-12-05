# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, exceptions
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleMakeDeposit(models.TransientModel):
    _name = "sale.make.deposit"
    _description = "Make deposit by Sales"

    amount = fields.Float('Down Payment Amount', digits=dp.get_precision('Account'),
                          help="The amount to be invoiced in advance, taxes excluded.")

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))[0]
        journal_ids = self.env['account.journal'].search([('type', '=', 'receive')])
        if not journal_ids:
            raise exceptions.UserError(u"ยังไม่มีการสร้างสมุดรายวันรับ")
        deposit_obj = self.env['bione.customer.deposit']
        new_deposit = {
            'date': fields.Date.context_today(self),
            'date_due': fields.Date.context_today(self),
            'customer_id': sale_orders.partner_id.id,
            'note': sale_orders.name ,
            'amount_receipt': self.amount,
            'journal_id': journal_ids[0].id,
            'sale_order_id': sale_orders.id,
        }
        payment_id = deposit_obj.create(new_deposit)
        deposit_line_obj = self.env['bione.customer.deposit.line']
        new_deposit_line = {
            'name': 'Down payment ' + sale_orders.name,
            'amount_receipt': self.amount,
            'payment_id': payment_id.id,
        }
        deposit_line_obj.create(new_deposit_line)
        action = self.env.ref('bione_thai_account.action_bione_customer_deposit').read()[0]
        action['views'] = [(self.env.ref('bione_thai_account.view_bione_customer_deposit_form').id, 'form')]
        action['res_id'] = payment_id.id
        return action
