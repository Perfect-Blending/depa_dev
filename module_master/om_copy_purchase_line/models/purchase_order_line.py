# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import api, models, fields, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    def copy_purchase_line(self):
        for line in self:
            line_id = line.with_context(default_order_id=line.order_id.id).copy()
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
