from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    department_id = fields.Many2one(comodel_name='hr.department',
                                    store=True,
                                    string='Department')
