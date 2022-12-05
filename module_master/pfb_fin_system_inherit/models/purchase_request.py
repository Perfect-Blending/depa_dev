from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    fin_number = fields.Many2one('fw_pfb_fin_system_100', 'Source Document')
    date_approve = fields.Datetime(string='Action Date',)
