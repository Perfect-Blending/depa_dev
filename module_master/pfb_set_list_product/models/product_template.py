from odoo import models, fields, api, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'


class StockRequestOrderInherit(models.Model):
    _inherit = 'stock.request.order'
