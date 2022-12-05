# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    secondary_uom_id = fields.Many2one('uom.uom',  string="Secondary UOM",compute="_quantity_compute_scrap",store=True)
    secondary_quantity = fields.Float(string='Secondary Qty',compute="_quantity_compute_scrap",store=True)


    @api.depends('product_id', 'scrap_qty')
    def _quantity_compute_scrap(self):
        for scrap in self:
            if scrap.product_id.is_secondary_uom:
                uom_quantity = scrap.product_id.uom_id._compute_quantity(scrap.scrap_qty, scrap.product_id.secondary_uom_id, rounding_method='HALF-UP')
                scrap.secondary_uom_id = scrap.product_id.secondary_uom_id
                scrap.secondary_quantity = uom_quantity


    def _prepare_move_values(self):
        self.ensure_one()
        return {
            'name': self.name,
            'origin': self.origin or self.picking_id.name or self.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.scrap_qty,
            'location_id': self.location_id.id,
            'scrapped': True,
            'location_dest_id': self.scrap_location_id.id,
            'move_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                           'product_uom_id': self.product_uom_id.id, 
                                           'qty_done': self.scrap_qty,
                                           'location_id': self.location_id.id, 
                                           'location_dest_id': self.scrap_location_id.id,
                                           'package_id': self.package_id.id, 
                                           'owner_id': self.owner_id.id,
                                           'lot_id': self.lot_id.id,
                                           'secondary_uom_id':  self.product_id.secondary_uom_id.id})],
#             'restrict_partner_id': self.owner_id.id,
            'picking_id': self.picking_id.id
        }

