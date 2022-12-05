# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2020 BiOne
#
##############################################################################

from odoo import models, fields


class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    inc_best_before_date = fields.Datetime(string="Best before")
    inc_removal_date = fields.Datetime(string="Removal Date")
    inc_alert_date = fields.Datetime(string="Alert Date")
    inc_life_date = fields.Datetime(string="End of Life Date")
    best_before_date = fields.Datetime(string="Best before",related="inc_best_before_date",store=True)
    removal_date = fields.Datetime(string="Removal Date",related="inc_removal_date",store=True)
    alert_date = fields.Datetime(string="Alert Date",related="inc_alert_date",store=True)
    life_date = fields.Datetime(string="End of Life Date",related="inc_life_date",store=True)


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _action_done(self):
        res = super(stock_move,self)._action_done()
        for each_move in res:
            picking_type_id = each_move.picking_type_id
            if picking_type_id.code == 'incoming' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                move_line_ids = each_move._get_move_lines()
                for move_line in move_line_ids.filtered(lambda l:l.tracking != 'none' and l.lot_id):
                    move_line.lot_id.write({'use_date':move_line.inc_best_before_date,'removal_date':move_line.inc_removal_date,
                        'alert_date':move_line.inc_alert_date, 'life_date':move_line.inc_life_date})
        return res

    def action_show_details(self):
        res = super(stock_move,self).action_show_details()
        context = res['context']
        res['context'].update({'show_expiry_field':True if self.picking_type_id.code == 'incoming' and not self.origin_returned_move_id.id and self.has_tracking != 'none' else False})
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(stock_move, self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        move_id = res.get('move_id')
        if move_id:
            move_id = self.env['stock.move'].browse(move_id)
            if move_id.has_tracking != 'none' and not move_id.origin_returned_move_id:
                picking_type_id = move_id.picking_type_id
                if picking_type_id.code == 'incoming' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                    dates = self.env['stock.production.lot']._get_dates(move_id.product_id.id)
                    res.update({'inc_best_before_date':dates['use_date'],'inc_removal_date':dates['removal_date'],
                        'inc_alert_date':dates['alert_date'], 'inc_life_date':dates['life_date']})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: