from odoo import api, fields, models

class bione_cheque_strike(models.Model):
    _name = 'bione.cheque.strike'

    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Note')