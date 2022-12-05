# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.


from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fin_purchase_id = fields.Many2one('fw_pfb_fin_system_purchase', string="FIN Purchase")
