# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import UserError

class fw_pfb_fin_product_template(models.Model):
    _inherit = 'product.template'

    fin_ok = fields.Boolean(string='Can be use as office expenses')
    pr_ok = fields.Boolean(string='Can be purchase request')

class fw_pfb_fin_sale_quote_template(models.Model):
    _inherit = 'sale.quote.template'

    fin_ok = fields.Boolean(string='Use in FIN 100')