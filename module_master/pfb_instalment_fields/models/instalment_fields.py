from odoo import models, fields, api, _


class WorkAcceptanceInherit(models.Model):
    _inherit = 'work.acceptance'

    instalment_wa = fields.Integer(string='Instalment')

    # cheque_no = fields.Char(string='Cheque No.', states={'draft': [('readonly', False)]}, readonly=True,)


