# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ReceiveClearCheque(models.TransientModel):
    _name = "receive.clear.cheque"

    date_clear = fields.Date(string='Clear Date', default=fields.Date.context_today, required=True)

    @api.multi
    def immediate_receive_clear_cheque(self):
        cheques = self.env['receive.cheque.master'].browse(self.env.context.get('active_ids'))
        for cheque_obj in cheques:
            if cheque_obj.state != 'deposited':
                raise UserError('You can clear only cheques already deposited !!!')
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_r_id.id
        interim_account = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not interim_account.interim_account_id:
            raise UserError(_('Set Customer Cheque Interim Account under Settings !!!'))
        for cheque_obj in cheques:
            line_ids = [
                (0, 0,
                 {'journal_id': journal_id, 'account_id': interim_account.interim_account_id.id, 'name': '/',
                  'partner_id': cheque_obj.partner_id.id,
                  'amount_currency': 0.0, 'credit': cheque_obj.amount}),
                (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id,
                        'name': cheque_obj.name + ' Clearance', 'amount_currency': 0.0, 'debit': cheque_obj.amount})
            ]
            vals = {
                'journal_id': journal_id,
                'ref': cheque_obj.name,
                'date': self.date_clear,
                'line_ids': line_ids,
            }
            account_move = self.env['account.move'].create(vals)
            account_move.post()
            cheque_obj.write(
                {'state': 'cleared', 'clear_date': self.date_clear, 'account_move_ids': [(4, account_move.id)], })

    @api.multi
    def receive_clear_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_r_id.id
        interim_account = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not interim_account.interim_account_id:
            raise UserError(_('Set Customer Cheque Interim Account under Settings !!!'))
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': interim_account.interim_account_id.id, 'name': '/',
              'partner_id': cheque_obj.partner_id.id,
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.account_id.id,
                    'name': cheque_obj.name + ' Clearance', 'amount_currency': 0.0, 'debit': cheque_obj.amount})
        ]
        vals = {
            'journal_id': journal_id,
            'ref': cheque_obj.name,
            'date': self.date_clear,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        cheque_obj.write({'state': 'cleared', 'clear_date': self.date_clear, 'account_move_ids': [(4, account_move.id)],})
