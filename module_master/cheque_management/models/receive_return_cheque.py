# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ReceiveReturnCheque(models.TransientModel):
    _name = "receive.return.cheque"

    date_return = fields.Date(string='Cheque Return Date', default=fields.Date.context_today, required=True)
    comment = fields.Text(string="Reason Of Return", required=True)

    @api.multi
    def return_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_r_id.id
        interim_account = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not interim_account.interim_account_id:
            raise UserError('Set Customer Cheque Interim Account under Settings !!!')
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': interim_account.interim_account_id.id, 'name': '/',
                'partner_id': cheque_obj.partner_id.id,
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.partner_account_id.id,
                    'partner_id': cheque_obj.partner_id.id,
                    'name': cheque_obj.name, 'amount_currency': 0.0, 'debit': cheque_obj.amount})
        ]
        vals = {
            'journal_id': journal_id,
            'ref': cheque_obj.name,
            'date': self.date_return,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        if cheque_obj.comment:
            comment = cheque_obj.comment+ "\n" + self.comment
        else:
            comment = self.comment
        cheque_obj.write({'state': 'returned', 'return_to_customer_date': self.date_return, 'comment': comment,'account_move_ids': [(4, account_move.id)],})
