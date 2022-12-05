# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################


from odoo import api, models, _, fields
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_custom = fields.Float(string='Quantity')

    @api.multi
    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            def check_product(x):
                for rec in line.product_id.pack_ids:
                    if x == rec.product_id:
                        return x
            
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                flag = False
                count = 0
                done_list = [] 
                deliver_list = []
                move_list = []
                products = []
                filtered = []
                picking_ids = self.env['stock.picking'].search([('origin','=',line.order_id.name)])
                for pick in picking_ids:
                    for move_is in pick.move_ids_without_package:
                        if move_is.product_id not in products:
                            products.append(move_is.product_id)
                pro = filter(check_product,products)
                for product in pro:
                    filtered.append(product)
                for pick in picking_ids:
                    for move_is in pick.move_ids_without_package: 
                        if move_is.product_id in filtered:
                            
                            if move_is.pack_id in line.product_id.pack_ids:
                                move_list.append(move_is.product_uom_qty)
                                done_list.append(move_is.quantity_done)

                stock_move = self.env['stock.move'].search([('origin','=',line.order_id.name)])
                if line.product_id.is_pack == True:
                    list_of_sub_product = []
                    for product_item in line.product_id.pack_ids:
                        list_of_sub_product.append(product_item.product_id)
                    for move in stock_move:
                        if count == 0:
                            if move.state == 'done' and move.product_uom_qty == move.quantity_done:
                                flag = True
                                for picking in picking_ids:
                                    for move_is in picking.move_ids_without_package:
                                        if sum(move_list) == 0:
                                            pass
                                        else: 
                                            deliver_qty =(line.product_uom_qty*sum(done_list))/sum(move_list)
                                            line.qty_delivered = int(deliver_qty)
                                            deliver_list.append(line.qty_delivered)        
                                          
                            elif move.state == 'confirmed':
                                flag = 'confirmed'
                                count = count+1
                                done_list.append(move.quantity_done)
                                for picking in picking_ids:
                                    for move_is in picking.move_ids_without_package:
                                        if sum(move_list) == 0:
                                            pass
                                        else:
                                            deliver_qty =(line.product_uom_qty*sum(done_list))/sum(move_list)
                                            line.qty_delivered = int(deliver_qty)
                                            deliver_list.append(line.qty_delivered)
                                        
                else:
                    for move in line.move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped and line.product_id == r.product_id):
                        if move.location_dest_id.usage == "customer":
                            if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                                qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
                        elif move.location_dest_id.usage != "customer" and move.to_refund:
                            qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
                    line.qty_delivered = qty                
   
    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_check_availability(self):
        res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        if self.product_id.is_pack:
            if self.product_id.type == 'product':
                warning_mess = {}
                for pack_product in self.product_id.pack_ids:
                    qty = self.product_uom_qty
                    if qty * pack_product.qty_uom > pack_product.product_id.virtual_available:
                        warning_mess = {
                                'title': _('Not enough inventory!'),
                                'message' : ('You plan to sell %s but you only have %s %s available, and the total quantity to sell is %s !' % (qty, pack_product.product_id.virtual_available, pack_product.product_id.name, qty * pack_product.qty_uom))
                                }
                        return {'warning': warning_mess}
        else:
            return res

    @api.multi
    def _action_launch_stock_rule(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
                continue
            qty = 0.0
            for move in line.move_ids:
                qty += move.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                group_line = line.order_id.procurement_group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
            if line.product_id.pack_ids:

                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
                product_qty = line.product_uom_qty - qty
                for val in values:
                    try:
                        pro_id = self.env['product.product'].browse(val.get('product_id'))
                        stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
                        product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
                        a = self.env['procurement.group'].run(pro_id, val.get('product_qty'), product_uom_obj, line.order_id.partner_shipping_id.property_stock_customer, val.get('name'), val.get('origin'), val)
                    except UserError as error:
                                errors.append(error.name)
            else:
                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
                product_qty = line.product_uom_qty - qty
                try:
                    self.env['procurement.group'].run(line.product_id, product_qty, line.product_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                except UserError as error:
                    errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def _prepare_procurement_values(self, group_id):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        values = []
        date_planned = datetime.strptime(str(self.order_id.confirmation_date), DEFAULT_SERVER_DATETIME_FORMAT)\
            + timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
        if  self.product_id.pack_ids:
            for item in self.product_id.pack_ids:
                line_route_ids = self.env['stock.location.route'].browse(self.route_id.id)
            
                values.append({
                    'name': item.product_id.name,
                    'origin': self.order_id.name,
                    'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_id': item.product_id.id,
                    'product_qty': item.qty_uom * abs(self.product_uom_qty),
                    'product_uom': item.uom_id and item.uom_id.id,
                    'company_id': self.order_id.company_id,
                    'group_id': group_id,
                    'sale_line_id': self.id,
                    'warehouse_id' : self.order_id.warehouse_id and self.order_id.warehouse_id,
                    'location_id': self.order_id.partner_shipping_id.property_stock_customer.id,
                    'route_ids': self.route_id and line_route_ids or [],
                    'partner_dest_id': self.order_id.partner_shipping_id,
                    'partner_id': self.order_id.partner_id.id,
                    'pack_id': item.id
                })
                    
            return values
        else:
            res.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'sale_line_id': self.id,
            'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_dest_id': self.order_id.partner_shipping_id
        })
        return res

    @api.multi
    def _get_delivered_qty(self):
        self.ensure_one()
        order = super(SaleOrderLine, self)._get_delivered_qty()
        picking_ids = self.env['stock.picking'].search([('origin','=',self.order_id.name)])
        list_of_picking = []
        list_of_pack_product = []
        for pic in picking_ids:
            list_of_picking.append(pic.id)
        if len(picking_ids) >= 1:
            if self.product_id.is_pack:
                for pack_item in self.product_id.pack_ids:
                    list_of_pack_product.append(pack_item.product_id.id)
                stock_move_ids = self.env['stock.move'].search([('product_id','in',list_of_pack_product),('picking_id','in',list_of_picking)])
                pack_delivered = all([move.state == 'done' for move in stock_move_ids])
                if pack_delivered:
                    return self.product_uom_qty
                else:
                    return 0.0
        return order

class ProcurementRule(models.Model):
    _inherit = 'stock.rule'

    def _run_pull(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if not self.location_src_id:
            msg = _('No source location defined on stock rule: %s!') % (self.name, )
            raise UserError(msg)

        # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        # Search if picking with move for it exists already:
        group_id = False
        if self.group_propagation_option == 'propagate':
            group_id = values.get('group_id', False) and values['group_id'].id
        elif self.group_propagation_option == 'fixed':
            group_id = self.group_id.id    

        data = self._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if values.get('pack_id'):
            data.update({'pack_id':values.get('pack_id')})
        # Since action_confirm launch following procurement_group we should activate it.
        move = self.env['stock.move'].sudo().with_context(force_company=data.get('company_id', False)).create(data)
        move._action_confirm()
        return True

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if product_id.pack_ids:
            for item in product_id.pack_ids:
                result.update({
                    'product_id': item.product_id.id,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'product_uom_qty': item.qty_uom,
                    'origin': origin,
                    'pack_id' : item.id,
                    })      
        return result
