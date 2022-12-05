# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class IssueCheque(models.Model):
    _name = "issue.cheque"

    cheque_id = fields.Many2one('cheque.master', string='Cheque Number', domain="[('state', '=', 'new')]", required=True)
    date_issue = fields.Date(string='Print Date', default=fields.Date.context_today, required=True)
    cheque_date = fields.Date(string='Cheque Date', required=True)
    partner_id = fields.Many2one('res.partner', string="Issued To", required=True)
    name_in_cheque = fields.Char(string="Name in Cheque", required=True)
    issue_journal_entry = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
    dest_account_id = fields.Many2one('account.account', string="Destination Account", required=True)
    amount = fields.Float('Amount', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('printed', 'Printed'),
    ], string='Status', readonly=True, default='new')

    @api.multi
    def copy(self):
        raise UserError(_('You cannot duplicate this record.'))

    @api.onchange('date_issue')
    def _onchange_date_issue(self):
        if self.date_issue and not self.cheque_date:
            self.cheque_date = self.date_issue

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.name_in_cheque = self.partner_id.name
            # print "kkkkkkkk", self.partner_id.name_get()
        if self.partner_id.customer:
            self.dest_account_id = self.partner_id.property_account_receivable_id
        elif self.partner_id.supplier:
            self.dest_account_id = self.partner_id.property_account_payable_id
        else:
            pass

    @api.model
    def create(self, vals):
        if vals['amount'] <= 0:
            raise UserError(_('Cheque amount must be greater than zero !!!'))
        self.env['cheque.master'].browse(vals['cheque_id']).write({'state': 'used',
                                                                   'partner_id': vals['partner_id'],
                                                                   'partner_account_id': vals['dest_account_id'],
                                                                   'date_issue': vals['date_issue'],
                                                                   'cheque_date': vals['cheque_date'],
                                                                   })
        vals['state'] = 'used'
        return super(IssueCheque, self).create(vals)

    @api.multi
    def post_cheque(self):
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_p_id:
            raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_p_id.id
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': self.cheque_id.bank_name.pdc_account_id.id, 'name': self.cheque_id.name,
              'amount_currency': 0.0, 'credit': self.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': self.dest_account_id.id, 'name': '/',
                    'amount_currency': 0.0, 'debit': self.amount, 'partner_id': self.partner_id.id})
        ]
        vals = {
            'journal_id': journal_id,
            'ref': self.cheque_id.name,
            'date': self.date_issue,
            'line_ids': line_ids,
        }
        # account_move = self.env['account.move'].create(vals)
        # account_move.post()
        # self.issue_journal_entry = account_move.id
        self.state = 'printed'
        self.cheque_id.write({'state': 'printed',
                              'date_issue': self.date_issue,
                              'cheque_date': self.cheque_date,
                              # 'account_move_ids': [(4, account_move.id)],
                              'partner_id': self.partner_id.id,
                              'partner_account_id': self.dest_account_id.id,
                              'amount': self.amount})

    # @api.multi
    # def print_cheque(self):
    #     print "printttt_chequeeeeee"
