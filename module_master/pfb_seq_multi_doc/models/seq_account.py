from odoo import fields, models


class hr(models.Model):
    _inherit = 'ir.sequence'

    account_active = fields.Boolean(
        'Use with Account',
        default=False
    )
