# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Rightechs (<http://www.Rightechs.net/>)
#               <contact@rightechs.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp
import time

class product_template(models.Model):
    _inherit = "product.template"

    def get_product_id(self):
        self.ensure_one()
        product_ids = self.env['product.product'].search([('product_tmpl_id','=', self.id)])
        return product_ids and product_ids[0] or False

    @api.multi
    def get_opening_balance(self):
        opening = []
        date_from = self.env.context.get('date_from', False)
        move_type = self.env.context.get('move_type', '1')

        opening_qty = 0
        opening_value = 0
        for template in self:
            product = template.get_product_id()
            if not product: return []

            orderby = " ORDER BY date ASC"
            where = '%s'%(product.id)
            query = """SELECT sm.product_qty,sm.value,pt.code FROM stock_move as sm
LEFT JOIN stock_picking_type AS pt ON pt.id=sm.picking_type_id
WHERE sm.product_id=%s AND sm.state in ('done') AND pt.code <> 'internal'"""
            if date_from:
                query += " AND date <= '%s'"
                where = (product.id,date_from)
            else:
                return [{'opening_qty': opening_qty, 'opening_value': opening_value}]
            if move_type == '2':
                query += " AND value <> 0"

            query += orderby
            self.env.cr.execute( query %where )
            data = self.env.cr.dictfetchall()

            for x in data:
                if not x['value']: x['value'] = 0.0

                if x['value'] >= 0:
                    opening_qty += x['product_qty']
                else:
                    opening_qty -= x['product_qty']
                opening_value += x['value']
        return [{'opening_qty': opening_qty, 'opening_value': round(opening_value,3)}]

    @api.multi
    def generate_stock_card(self):
        date_from = self.env.context.get('date_from', False)
        date_to = self.env.context.get('date_to', False)
        move_type = self.env.context.get('move_type', '1')

        for template in self:
            product = template.get_product_id()
            if not product: return []
            print ("\n\n******** PRODUCT **********", product.name,product.id)
            orderby = " ORDER BY sm.date ASC"
            where = '%s'%(product.id)
            query = '''SELECT 
                            sm.id,t.name as product,sm.reference,sm.date,sm.product_qty,sm.price_unit,
                            sm.value,sm.remaining_qty,sm.remaining_value,pt.code as operation,sm.picking_type_id,
                            sm.product_id,sm.origin, l.name as location
                        FROM stock_move AS sm
                        LEFT JOIN product_product AS p ON p.id=sm.product_id
                        LEFT JOIN product_template AS t ON t.id=p.product_tmpl_id
                        LEFT JOIN stock_picking_type AS pt ON pt.id=sm.picking_type_id
                        LEFT JOIN stock_location as l on l.id=sm.location_id
                        WHERE sm.product_id=%s and sm.state in ('done')'''
            if date_from:
                query += " AND sm.date >= '%s'"
                where = (product.id,date_from)
            if date_to:
                query += " AND sm.date <= '%s'"
                where = (product.id,date_from,date_to)
            if move_type == '2':
                query += " AND sm.value <> 0"

            query += orderby
            self.env.cr.execute( query %where )
            data = self.env.cr.dictfetchall()

            data = template.rearrange(data)
            print ("\n***********\nFINAL RESULT: -----------> ", data)
        return data

    def rearrange(self, data=[]):
        data_list = []
        remaining_qty = 0.0
        remaining_value = 0.0
        balance = self.get_opening_balance()
        balance_qty = balance[0]['opening_qty']
        balance_value = balance[0]['opening_value']
        if not data: return data_list

        last_record = {'remaining_qty': 0.0, 'remaining_value': 0.0, 
                       'balance_qty': 0.0, 'balance_value': 0.0}

        for element in data:
            print("\nELEMENT: ----> ", element['operation'],element['product_qty'],element['value'])#,element['remaining_qty'],element['remaining_value']
            if 'remaining_qty' not in element: element.update({'remaining_qty': 0.0})
            if 'remaining_value' not in element or not element['remaining_value']: element.update({'remaining_value': 0.0})
            if 'balance_qty' not in element: element.update({'balance_qty': 0.0})
            if 'balance_value' not in element: element.update({'balance_value': 0.0})
            if 'inqty' not in element: element.update({'inqty': 0.0})
            if 'outqty' not in element: element.update({'outqty': 0.0})
            element['price_unit'] = element['price_unit'] and round( element['price_unit'], 2) or 0.0
            if element['value'] is None: element['value'] = 0.0
            if element['remaining_qty'] is None: element['remaining_qty'] = 0.0

            element['value'] = float('%.3f'% element['value'])
            element['remaining_value'] = float('%.3f'% element['remaining_value'])
            element['inqty'] = float('%.3f'% element['inqty'])
            element['remaining_qty'] = float('%.3f'% element['remaining_qty'])
            element['outqty'] = float('%.3f'% element['outqty'])
            element['balance_qty'] = float('%.3f'% element['balance_qty'])
            element['balance_value'] = float('%.3f'% element['balance_value'])
            element['price_unit'] = float('%.3f'% element['price_unit'])
            res = element.copy()
            #INCOMING MOVE
            if element['value'] > 0:
                balance_qty += element['product_qty']
                balance_value += element['value'] or 0.0

                updation = {'balance_qty': balance_qty,
                            'balance_value': balance_value}

                res.update({'inqty': element['product_qty']})
                res.update(updation)
                last_record.update(updation)

            #OUTGOING MOVE
            elif element['value'] < 0:
                balance_qty -= element['product_qty']
                balance_value += element['value'] or 0.0

                updation = {'balance_qty': balance_qty,
                            'balance_value': balance_value}

                res.update({'outqty': element['product_qty']})
                res.update(updation)
                last_record.update(updation)

            #OTHER/Internal MOVES
            else:
                if element['operation'] == 'internal':
                    res.update({'inqty': element['product_qty'],
                                'outqty': -element['product_qty'],
                                'balance_qty': last_record.get('balance_qty'),
                                'balance_value': last_record.get('balance_value')})
            data_list.append(res)
        return data_list

