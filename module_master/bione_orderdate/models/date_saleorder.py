from odoo import fields, models


class DateSaleOrder(models.Model):

    _inherit = 'sale.order'

    date_saleorder = fields.Datetime(string="Order Date", required=False, )