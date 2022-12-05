# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.

from odoo import api, fields, models, _


class fw_pfb_fin_settings2(models.Model):
    _inherit = 'fw_pfb_fin_settings2'

    default_fin_purchase_partner_id = fields.Many2one('res.partner', string="Default Partner for FIN Puchase")
