# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReceiveACheque(models.TransientModel):
    _name = "receive.cheque2"

    name = fields.Char(string='Cheque No.', required=True)
    partner_id = fields.Many2one('res.partner', string="Receiving From", required=True)
    partner_account_id = fields.Many2one('account.account', string="Partner Account", required=True)
    received_date = fields.Date(string='Receiving Date', required=True, default=fields.Date.context_today)
    cheque_date = fields.Date(string='Cheque Date', required=True, default=fields.Date.context_today)
    bank_name = fields.Many2one('customer.bank', string='Customer Bank Name', required=True)
    amount = fields.Float('Amount', required=True)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id.customer:
            self.partner_account_id = self.partner_id.property_account_receivable_id
        elif self.partner_id.supplier:
            self.partner_account_id = self.partner_id.property_account_payable_id
        else:
            pass

    @api.multi
    def receive_cheque(self):
        if self.amount <= 0:
            raise UserError(_('Cheque amount must be greater than zero !!!'))
        cheque_master = self.env['receive.cheque.master']
        search_ids = cheque_master.search([('name', '=', self.name),
                                           ('partner_id', '=', self.partner_id.id),
                                           ('bank_name', '=', self.bank_name.id)])
        if search_ids:
            raise UserError(_('Cheque with same details already Received. Please check given details !!!'))
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_r_id.id
        interim_account = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not interim_account.interim_account_id:
            raise UserError(_('Set Customer Cheque Interim Account under Settings !!!'))
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': self.partner_account_id.id,
              'name': self.name, 'partner_id': self.partner_id.id,
              'amount_currency': 0.0, 'credit': self.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': interim_account.interim_account_id.id, 'name': self.name,
                    'amount_currency': 0.0, 'partner_id': self.partner_id.id, 'debit': self.amount})
        ]
        values = {
            'journal_id': journal_id,
            'ref': self.name,
            'date': self.received_date,
            'line_ids': line_ids,
        }
        # account_move = self.env['account.move'].create(values)
        # account_move.post()
        vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'partner_account_id': self.partner_account_id.id,
            'received_date': self.received_date,
            'cheque_date': self.cheque_date,
            'amount': self.amount,
            'bank_name': self.bank_name.id,
            'state': 'received',
            # 'account_move_ids': [(6, 0, [account_move.id])],
        }
        cheque_master.create(vals)

    @api.multi
    def action_clear(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receive A Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'receive.cheque2',
            'target': 'new',
            'context': 'None'
        }
