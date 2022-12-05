# -*- coding: utf-8 -*-
from odoo import models, fields



class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_enable_order_note = fields.Boolean('Order Note')
    pos_enable_product_note = fields.Boolean('Product Line Note')
    is_pos_order_note_receipt = fields.Boolean('Order Note on Receipt')
    is_pos_product_note_receipt = fields.Boolean('Product Line Note on Receipt')


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    line_note = fields.Char('Note')


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _order_fields(self,vals):
        res = super(PosOrder, self)._order_fields(vals)
        res.update({
            'note': vals.get('order_note') or False
        })
        return res
