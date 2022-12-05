from odoo import fields, models, api


class AccountMoveSumLine(models.Model):
    _name = 'bione.account_move_sum_line'
    _order = 'seq asc'

    move_id = fields.Many2one('account.move')

    account_id = fields.Many2one('account.account', string='Account')
    name = fields.Char('Description')
    currency_id = fields.Many2one('res.currency', string='Currency')
    debit = fields.Monetary('Debit')
    credit = fields.Monetary('Credit')
    seq = fields.Integer()
    


