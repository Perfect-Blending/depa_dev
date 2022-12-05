# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import time

class AccountCashMove(models.Model):
    _name = 'account.cash.move'
    _description = 'Cash Move'
    _order = 'date desc, id desc'

    REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    # payment_id = fields.Many2one('account.payment', string='Payment.', readonly=True, ondelete='cascade', index=True)
    advance_id = fields.Many2one('account.advance', string='Advance', ondeleted='cascade',index=True)
    advance_clear_id = fields.Many2one('account.advance.clear', string='Advance clear', ondeleted='cascade',index=True)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True,index=True )
    petty_id = fields.Many2one("account.petty.payment","Payment",required=False,index=True)
    fund_id = fields.Many2one("account.petty.fund","Petty Cash Fund",index=True)
    # name = fields.Char(string='Doc No.', size=64,
    #     default=lambda self: self._context.get('name',"/"),index=True)
    amount = fields.Float(string='Amount', required=True, digits=0)
    # amount = fields.Monetary(string='Amount',  required=True)
    #amount = fields.Float(string='Amount', required=True, digits='Account',
        #default=get_amount)
    type = fields.Selection([('in','In'), ('out', 'Out')], string='Type', required=True,index=True,
        default=lambda self: self._context.get('type',False))
    note = fields.Text('Notes',)
    account_id = fields.Many2one('account.account', string='Account', required=True,domain=[('deprecated', '=', False)],index=True)
    date = fields.Date(string='Date', required=True,
        default=lambda self: self._context.get('date', time.strftime("%Y-%m-%d")),index=True)
    state = fields.Selection(
        [ ('draft','Draft')
        , ('posted','Post')
        , ('canceled','Canceled')
        ], string='State', required=True, default="draft",index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,index=True,
        default=lambda self: self.env.user.company_id)

    @api.onchange('fund_id')
    def onchange_petty_cash(self):
        self.account_id = self.fund_id.account_id

    def button_cancel(self):
        if not self:
           return
        self._cr.execute(""" update account_cash_move set state='canceled' where id = %s """%(self.id))
        return True

