# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, api,_
from datetime import date
from datetime import datetime

from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning, UserError


class sales_daybook_product_category_report(models.AbstractModel):
    _name = 'report.bi_inventory_valuation_fifo_report.inv_template'
    
    @api.multi
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        docs = self.env['sale.day.book.wizard'].browse(docids)
        data  = {'filter_by':docs.filter_by, 'start_date': docs.start_date, 'end_date': docs.end_date,'product_ids':docs.product_ids ,'warehouse':docs.warehouse,'category':docs.category,'location_id':docs.location_id,'company_id':docs.company_id.name,'display_sum':docs.display_sum,'currency':docs.company_id.currency_id.name}
        return {
                   'doc_model': 'sale.day.book.wizard',
                   'data' : data,
                   'get_warehouse' : self._get_warehouse_name,
                   'get_lines':self._get_lines,
                   'get_data' : self._get_data,
                   }

    def _get_warehouse_name(self,data):
        if data:
            l1 = []
            l2 = []
            for i in data:
                l1.append(i.name)
                myString = ",".join(l1 )
            return myString
        return ''
    
    def _get_company(self, data):
        if data['company_id']:
            l1 = []
            l2 = []
            obj = self.env['res.company'].search([('name', '=', data['company_id'])])
            l1.append(obj.name)
            return l1
        return ''

    def _get_currency(self,data):
        if data['company_id']:
            l1 = []
            l2 = []
            obj = self.env['res.company'].search([('name', '=', data['company_id'])])
            l1.append(obj.currency_id.name)
            return l1
        return ''
    


    def _compute_stock_value(self,product_obj,to_date):
        StockMove = self.env['stock.move']
        #to_date = self.env.context.get('to_date')

        
        real_time_product_ids = [product.id for product in product_obj if product.product_tmpl_id.valuation == 'real_time']
        if real_time_product_ids:
            self.env['account.move.line'].check_access_rights('read')
            fifo_automated_values = {}
            query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), sum(quantity), array_agg(aml.id)
                         FROM account_move_line AS aml
                        WHERE aml.product_id IN %%s AND aml.company_id=%%s %s
                     GROUP BY aml.product_id, aml.account_id"""
            params = (tuple(real_time_product_ids), self.env.user.company_id.id)
            if to_date:
                query = query % ('AND aml.date <= %s',)
                params = params + (to_date,)
            else:
                query = query % ('',)
            self.env.cr.execute(query, params=params)

            res = self.env.cr.fetchall()
            for row in res:
                fifo_automated_values[(row[0], row[1])] = (row[2], row[3], list(row[4]))

        product_values = {product.id: 0 for product in product_obj}
        product_move_ids = {product.id: [] for product in product_obj}

        if to_date:
            domain = [('product_id', 'in', product_obj.ids), ('date', '<=', to_date)] + StockMove._get_all_base_domain()
            value_field_name = 'value'
        else:
            domain = [('product_id', 'in', product_obj.ids)] + StockMove._get_all_base_domain()
            value_field_name = 'remaining_value'

        StockMove.check_access_rights('read')
        query = StockMove._where_calc(domain)
        StockMove._apply_ir_rules(query, 'read')
        from_clause, where_clause, params = query.get_sql()
        query_str = """
            SELECT stock_move.product_id, SUM(COALESCE(stock_move.{}, 0.0)), ARRAY_AGG(stock_move.id)
            FROM {}
            WHERE {}
            GROUP BY stock_move.product_id
        """.format(value_field_name, from_clause, where_clause)
        self.env.cr.execute(query_str, params)
        for product_id, value, move_ids in self.env.cr.fetchall():
            product_values[product_id] = value
            product_move_ids[product_id] = move_ids

        for product in product_obj:
            if product.cost_method in ['standard', 'average']:
                qty_available = product.with_context(company_owned=True, owner_id=False).qty_available
                price_used = product.standard_price
                if to_date:
                    price_used = product.get_history_price(
                        self.env.user.company_id.id,
                        date=to_date,
                    )
                
                product.stock_value = price_used * qty_available
                product.qty_at_date = qty_available
            elif product.cost_method == 'fifo':
                if to_date:
                    if product.product_tmpl_id.valuation == 'manual_periodic':
                        product.stock_value = product_values[product.id]
                        product.qty_at_date = product.with_context(to_date=to_date,company_owned=True, owner_id=False).qty_available
                        product.stock_fifo_manual_move_ids = StockMove.browse(product_move_ids[product.id])
                        return product.qty_at_date
                    elif product.product_tmpl_id.valuation == 'real_time':
                        valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                        value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, [])
                        return quantity
                        product.stock_value = value
                        product.qty_at_date = quantity
                        product.stock_fifo_real_time_aml_ids = self.env['account.move.line'].browse(aml_ids)
                else:
                    product.stock_value = product_values[product.id]
                    product.qty_at_date = product.with_context(company_owned=True, owner_id=False).qty_available
                    if product.product_tmpl_id.valuation == 'manual_periodic':
                        product.stock_fifo_manual_move_ids = StockMove.browse(product_move_ids[product.id])
                    elif product.product_tmpl_id.valuation == 'real_time':
                        valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                        value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, [])
                        product.stock_fifo_real_time_aml_ids = self.env['account.move.line'].browse(aml_ids)





    def _get_lines(self, data):
            product_res = self.env['product.product'].search([('qty_available', '!=', 0),
                                                                ('type', '=', 'product'),

                                                                ])
            category_lst = []
            if data['category'] and data['filter_by'] == 'categ':

                for cate in data['category'] :
                    if cate.id not in category_lst :
                        
                        category_lst.append(cate.id)
                       
                    for child in  cate.child_id :
                        if child.id not in category_lst :
                            category_lst.append(child.id)

            


            if len(category_lst) > 0 :

                product_res = self.env['product.product'].search([('categ_id','in',category_lst),('qty_available', '!=', 0),('type', '=', 'product')])
                


            lines = {}

            if data['product_ids'] and data['filter_by'] == 'product':
                product_res = data['product_ids']
            
            for product in  product_res :
                

                if product.categ_id.property_cost_method == 'fifo' :

                    fifo_moves = product.with_context(to_date=data['start_date']).stock_fifo_manual_move_ids
                    
                    sales_value = 0.0
                    incoming = 0.0
                    custom_domain = []
                    if data['company_id']:
                        obj = self.env['res.company'].search([('name', '=', data['company_id'])])
                        
                        custom_domain.append(('company_id','=',obj.id))


                    if data['warehouse'] :
                        warehouse_lst = [a.id for a in data['warehouse']]
                        custom_domain.append(('picking_id.picking_type_id.warehouse_id','in',warehouse_lst))

                    if data['location_id'] :
                        custom_domain.append('|')
                        custom_domain.append(('location_dest_id','=',data['location_id'].id))
                        custom_domain.append(('location_id','=',data['location_id'].id))


                    fifo_vals = {}
                    to_date = datetime.combine(data['start_date'], datetime.min.time())
                    qty_date = self._compute_stock_value(product,to_date)
                    
                    
                    stock_move_line = self.env['stock.move'].search([
                        ('product_id','=',product.id),
                        ('date','>=',data['start_date']),
                        ('date',"<=",data['end_date']),
                        ('state','=','done')
                        ] + custom_domain)

                    
                    
                    for move in stock_move_line :


                        if move.picking_id.picking_type_id.code == "internal" :
                            cost_unit = 0
                            if move.location_id == data['location_id'] :

                                cost_unit =  - product.standard_price
                                qty_date = qty_date - move.product_uom_qty

                            if move.location_dest_id == data['location_id'] :

                                cost_unit =   product.standard_price
                                qty_date = qty_date + move.product_uom_qty


                            
                            
                            if move.picking_id.name not in  fifo_vals :

                                vals = {
                                    'sku': product.default_code or '',
                                    'name': product.name or '',
                                    'category': product.categ_id.name or '' ,
                                    'cost_price': cost_unit or 0,
                                    'available':  0 ,
                                    'virtual':   0,
                                    'incoming':  0,
                                    'outgoing':  0,
                                    'net_on_hand':   move.product_uom_qty,
                                    'total_value': move.product_uom_qty * cost_unit or 0,
                                    'adjust':  0,
                                    'purchase_value':  0,
                                    'type':  'Internal',
                                    'internal': move.product_uom_qty,
                                    'price_unit' : move.price_unit,
                                    'qty_date' : qty_date,
                                     'date' : move.date
                                }
                                fifo_vals.update({move.picking_id.name :vals })


                        if move.inventory_id :
                            
                            adjust = move.product_uom_qty
                            if move.value >= 0 :
                                qty_date = qty_date + adjust
                            else :
                                qty_date = qty_date - adjust


                            if move.reference not in  fifo_vals :

                                vals = {
                                    'sku': product.default_code or '',
                                    'name': product.name or '',
                                    'category': product.categ_id.name or '' ,
                                    'cost_price': move.price_unit or 0,
                                    'available':  0 ,
                                    'virtual':   0,
                                    'incoming':  0,
                                    'outgoing':  0,
                                    'net_on_hand':   move.product_uom_qty,
                                    'total_value':  move.value or 0,
                                    'adjust':  move.product_uom_qty,
                                    'purchase_value':  0,
                                    'type':  'Adjustments',
                                    'internal': 0,
                                    'price_unit' : move.price_unit,
                                    'qty_date' : qty_date,
                                    'date' : move.date
                                }
                                fifo_vals.update({move.reference  :vals })
                        
                        
                        if move.picking_id.picking_type_id.code == "outgoing" :
                            if data['location_id'] :
                                locations_lst = [data['location_id'].id]
                                for i in data['location_id'].child_ids :
                                    locations_lst.append(i.id)
                                if move.location_id.id in locations_lst :
                                    sales_value = sales_value + move.product_uom_qty

                            else :

                                sales_value = sales_value + move.product_uom_qty
                            qty_date = qty_date - move.product_uom_qty
                            if move.picking_id.name not in  fifo_vals :

                                vals = {
                                    'sku': product.default_code or '',
                                    'name': product.name or '',
                                    'category': product.categ_id.name or '' ,
                                    'cost_price': move.price_unit or 0,
                                    'available':  0 ,
                                    'virtual':   0,
                                    'incoming':  0,
                                    'outgoing':  move.product_uom_qty,
                                    'net_on_hand':   move.product_uom_qty,
                                    'total_value': move.value or 0,
                                    'adjust':  0,
                                    'purchase_value':  0,
                                    'type':  'Outgoing',
                                    'internal': 0,
                                    'price_unit' : move.price_unit,
                                    'qty_date' : qty_date,
                                     'date' : move.date
                                }
                                fifo_vals.update({move.picking_id.name :vals })

                        if move.picking_id.picking_type_id.code == "incoming" :

                            qty_date = qty_date + move.product_uom_qty
                            if move.picking_id.name not in  fifo_vals :

                                vals = {
                                    'sku': product.default_code or '',
                                    'name': product.name or '',
                                    'category': product.categ_id.name or '' ,
                                    'cost_price': move.price_unit or 0,
                                    'available':  0 ,
                                    'virtual':   0,
                                    'incoming':  move.product_uom_qty,
                                    'outgoing':  0,
                                    'net_on_hand':   move.product_uom_qty,
                                    'total_value':  move.value or 0,
                                    'adjust':  0,
                                    'purchase_value':  0,
                                    'type':  'Incoming',
                                    'internal': 0,
                                    'price_unit' : move.price_unit,
                                    'qty_date' : qty_date,
                                     'date' : move.date
                                }
                                fifo_vals.update({move.picking_id.name :vals })
                            if data['location_id'] :
                                locations_lst = [data['location_id'].id]
                                for i in data['location_id'].child_ids :
                                    locations_lst.append(i.id)
                                if move.location_dest_id.id in locations_lst :
                                    incoming = incoming + move.product_uom_qty


                            else :


                                incoming = incoming + move.product_uom_qty


                    
                    
                    lines.update({product.name : fifo_vals})  


            return lines



    def _get_data(self,data):
        product_res = self.env['product.product'].search([('qty_available', '!=', 0),
                                                                ('type', '=', 'product'),

                                                                ])
        category_lst = []
        fifo_vals = {}
        incoming = 0
        sales_value = 0
        if data['category'] :

            for cate in data['category'] :
                if cate.id not in category_lst :
                   category_lst.append(cate.id)
                   
                for child in  cate.child_id :
                    if child.id not in category_lst :
                        category_lst.append(child.id)

        if len(category_lst) > 0 :

            product_res = self.env['product.product'].search([('categ_id','in',category_lst),('qty_available', '!=', 0),('type', '=', 'product')])
                
        lines = []
        if data['product_ids'] :
                product_res = data['product_ids']
        for product in  product_res :
            if product.categ_id.property_cost_method == 'fifo' :
                custom_domain = []
                if data['company_id']:
                    obj = self.env['res.company'].search([('name', '=', data['company_id'])])
                    
                    custom_domain.append(('company_id','=',obj.id))


                if data['warehouse'] :
                    warehouse_lst = [a.id for a in data['warehouse']]
                    custom_domain.append(('picking_id.picking_type_id.warehouse_id','in',warehouse_lst))

                if data['location_id'] :
                    custom_domain.append('|')
                    custom_domain.append(('location_dest_id','=',data['location_id'].id))
                    custom_domain.append(('location_id','=',data['location_id'].id))

                stock_move_line = self.env['stock.move'].search([
                    ('product_id','=',product.id),
                    ('picking_id.date_done','>=',data['start_date']),
                    ('picking_id.date_done',"<=",data['end_date']),
                    ('state','=','done')
                    ] + custom_domain)


                for move in stock_move_line :


                    if move.picking_id.picking_type_id.code == "internal" :

                        cost_unit = 0
                        if move.location_id == data['location_id'] :

                            cost_unit =  - product.standard_price
                            

                        if move.location_dest_id == data['location_id'] :

                            cost_unit =   product.standard_price
                            


                        if product.categ_id.name not in  fifo_vals :

                            vals = {
                                
                                
                                
                                'incoming':  0,
                                'outgoing':  0,
                                'net_on_hand':   move.product_uom_qty,
                                'total_value': cost_unit * move.product_uom_qty or 0,
                                'adjust':  0,
                                'purchase_value':  0,
                                'type':  'Internal',
                                'internal': move.product_uom_qty,
                                
                            }
                            fifo_vals.update({product.categ_id.name :vals })

                        else :
                            fifo_vals.get(product.categ_id.name).update({'internal' :fifo_vals.get(product.categ_id.name).get('internal') + move.product_uom_qty,
                                                                        'total_value' : fifo_vals.get(product.categ_id.name).get('total_value') + cost_unit * move.product_uom_qty })

                            
                    if move.picking_id.picking_type_id.code == "outgoing" :
                        if data['location_id'] :
                            locations_lst = [data['location_id'].id]
                            for i in data['location_id'].child_ids :
                                locations_lst.append(i.id)
                            if move.location_id.id in locations_lst :
                                sales_value = sales_value + move.product_uom_qty

                        else :

                            sales_value = sales_value + move.product_uom_qty

                        if product.categ_id.name not in  fifo_vals :

                            vals = {
                                
                                
                                
                                'incoming':  0,
                                'outgoing':  move.product_uom_qty,
                                'net_on_hand':   move.product_uom_qty,
                                'total_value': move.value or 0,
                                'adjust':  0,
                                'purchase_value':  0,
                                'type':  'Outgoing',
                                'internal': 0,
                                
                            }
                            fifo_vals.update({product.categ_id.name :vals })

                        else :
                            fifo_vals.get(product.categ_id.name).update({'outgoing' :fifo_vals.get(product.categ_id.name).get('outgoing') + move.product_uom_qty,
                                                                        'total_value' : fifo_vals.get(product.categ_id.name).get('total_value') + move.value })

                    if move.picking_id.picking_type_id.code == "incoming" :
                        if product.categ_id.name not in  fifo_vals :

                            vals = {
                                
                                'incoming':  move.product_uom_qty,
                                'outgoing':  0,
                                'net_on_hand':   move.product_uom_qty,
                                'total_value':  move.value or 0,
                                'adjust':  0,
                                'purchase_value':  0,
                                'type':  'Incoming',
                                'internal': 0,
                                
                            }
                            fifo_vals.update({product.categ_id.name :vals })

                        else :
                            fifo_vals.get(product.categ_id.name).update({'incoming' :fifo_vals.get(product.categ_id.name).get('incoming') + move.product_uom_qty,
                                                                        'total_value' : fifo_vals.get(product.categ_id.name).get('total_value') + move.value })
                        if data['location_id'] :
                            locations_lst = [data['location_id'].id]
                            for i in data['location_id'].child_ids :
                                locations_lst.append(i.id)
                            if move.location_dest_id.id in locations_lst :
                                incoming = incoming + move.product_uom_qty


                        else :


                            incoming = incoming + move.product_uom_qty

                if data['location_id'] :
                    custom_domain.append('|')
                    custom_domain.append(('location_dest_id','=',data['location_id'].id))
                    custom_domain.append(('location_id','=',data['location_id'].id))


                inventory_domain = [
                    ('date','>=',data['start_date']),
                    ('date',"<=",data['end_date'])

                    ] 
                stock_pick_lines = self.env['stock.move'].search([('product_id.id','=',product.id)] + inventory_domain + custom_domain)
                stock_internal_lines = self.env['stock.move'].search([('location_id.usage', '=', 'internal'),('location_dest_id.usage', '=', 'internal'),('product_id.id','=',product.id)] + inventory_domain)
                
                adjust = 0
                internal = 0
                plus_picking = 0
                
                if stock_pick_lines:
                    for invent in stock_pick_lines:

                        if invent.inventory_id :
                        
                            adjust = invent.product_uom_qty

                            if product.categ_id.name not in  fifo_vals :

                                vals = {
                                    
                                    'incoming':  0,
                                    'outgoing':  0,
                                    'net_on_hand':   invent.product_uom_qty,
                                    'total_value':  invent.value or 0,
                                    'adjust':  invent.product_uom_qty,
                                    'purchase_value':  0,
                                    'type':  'Inventory',
                                    'internal': 0,
                                    'price_unit' : invent.price_unit
                                }
                                fifo_vals.update({product.categ_id.name  :vals })
                            else :
                                fifo_vals.get(product.categ_id.name).update({'adjust' :fifo_vals.get(product.categ_id.name).get('adjust') + invent.product_uom_qty,
                                                                        'total_value' : fifo_vals.get(product.categ_id.name).get('total_value') + invent.value })
                if stock_internal_lines:

                    for inter in stock_internal_lines:
                        
                        internal = inter.product_uom_qty


        return fifo_vals
            

























    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
