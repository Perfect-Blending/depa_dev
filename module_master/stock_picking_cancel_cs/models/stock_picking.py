from odoo import api, fields, models, exceptions
from odoo.tools.float_utils import float_round, float_compare, float_is_zero 


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking):

        vals = super(ReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        if self._context.get('cancel_return_fifo'):
            vals.update({
                'value': abs(return_line.move_id.price_unit * return_line.move_id.quantity_done) or 0.00,
                'price_unit': abs(return_line.move_id.price_unit) or 0.00
            })
        return vals


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cancel_done_picking = fields.Boolean(string='Cancel Done Delivery?', compute='check_cancel_done_picking')
    return_picking_id = fields.Many2one('stock.picking')


    @api.model
    def check_cancel_done_picking(self):

        for picking in self:
            if picking.company_id.cancel_done_picking:
                picking.cancel_done_picking = True

    @api.multi
    def action_cancel(self):
        quant_obj = self.env['stock.quant']
        stock_mv_obj = in_moves = out_moves = self.env['stock.move'] 
        moves = self.env['account.move']
        pick_obj = self.env['stock.picking']
        return_picking_obj = self.env['stock.return.picking']
        account_move_obj = self.env['account.move']
        res = True
        imediate_obj = self.env['stock.immediate.transfer']
        if self.env.context.get('Flag', False):
            for picking in self:
                if picking.state == 'done':
                    account_moves = picking.move_lines
                    flag = False
                    if picking.origin and 'Return' in picking.origin : 
                        flag = True
                    if picking.product_id.categ_id.property_cost_method == 'fifo' and not flag and not picking.return_picking_id:
                        product_return_moves =[]
                        move_dest_exists = False
                        for move in account_moves:
                            if move.state == 'cancel':
                                continue
                            if move.scrapped:
                                continue
                            if move.move_dest_ids:
                                move_dest_exists = True
                            quantity = move.product_qty - sum(move.move_dest_ids.filtered(
                                lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('move_line_ids').mapped('product_qty'))
                            quantity = float_round(quantity, precision_rounding=move.product_uom.rounding)
                            product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'move_id': move.id, 'uom_id': move.product_id.uom_id.id}))
                        location_id = picking.location_id.id
                        if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                            location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                        if product_return_moves:
                            return_pick = return_picking_obj.with_context(active_id=picking.id).create({
                                'picking_id': picking.id,
                                'product_return_moves': product_return_moves,
                                'move_dest_exists': move_dest_exists,
                                'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id,
                                'original_location_id': picking.location_id.id,
                                'location_id': location_id,

                            })                        
                            new_picking,type = return_pick.with_context(cancel_return_fifo=True)._create_returns()
                            return_pick.return_picking_id = new_picking
                            new_pick = pick_obj.browse(new_picking)
                            new_pick.action_confirm()
                            new_pick.action_assign()
                            imediate_rec = imediate_obj.create({'pick_ids': [(4, new_pick.id)]})
                            imediate_rec.process()
                            if new_pick.state != 'done':
                                for move in new_pick.move_ids_without_package:
                                    move.quantity_done = move.product_uom_qty
                                new_pick.button_validate()

                    else:
                        for move in account_moves:
                            if move.state == 'cancel':
                                continue
                            landed_cost_rec = []
                            try:
                                landed_cost_rec= self.env['stock.landed.cost'].search(
                                    [('picking_ids', '=', picking.id), ('state', '=', 'done')])
                            except:
                                pass

                            if landed_cost_rec:
                                raise exceptions.Warning('This Delivery is set in landed cost record %s you need to delete it fisrt then you can cancel this Delivery'%','.join(landed_cost_rec.mapped('name')))

                            if move.state == "done" and move.product_id.type == "product":
                                for move_line in move.move_line_ids:
                                    quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                                    quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity, move_line.lot_id, move_line.package_id, move_line.owner_id)
                                    quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id, quantity * -1, move_line.lot_id, move_line.package_id, move_line.owner_id)
                                    
                            if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                                move.state = 'waiting'
                            elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                                move.state = 'waiting'
                            else:
                                move.state = 'confirmed'
                            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                            if move.propagate:
                                if all(state == 'cancel' for state in siblings_states):
                                    move.move_dest_ids._action_cancel()
                            else:
                                if all(state in ('done', 'cancel') for state in siblings_states):
                                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                                move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})

                            account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])

                            for account_move in account_moves:
                                account_move.line_ids.sudo().remove_move_reconcile()
                                account_move.button_cancel()
                                account_move.unlink()
                res = super(StockPicking, picking).action_cancel()
        else:    
            res = super(StockPicking, self).action_cancel()

        return res

    @api.multi
    def action_draft(self):
        for res in self:
            if res.state == 'cancel' :
                res.state = 'draft'
                res.move_lines.write({'state':'draft'})
        return True
