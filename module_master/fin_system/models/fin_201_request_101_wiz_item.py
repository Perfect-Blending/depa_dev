# -*- coding: utf-8 -*- 
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-Now Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import date

FIN_TYPE_PULL_FIN100 = [('eroe', 'Expense request of express'),
                   ('erob', 'Expense request of budget'),
                   ('proo', 'Purchase reguest of objective'),
                   ('parr', 'Payment and refund request')]

class fin_201_request_101_wiz_item(models.TransientModel):
    _name = 'fin_201_request_101_wiz_item'

    '''
    fields
    '''
    fin_type = fields.Selection(FIN_TYPE_PULL_FIN100, string='FIN Type')
    wiz_id = fields.Many2one('fin_201_request_101_wiz',string=_("Wizard request"))  
    select = fields.Boolean(string=_("Select"))
    fin_line_id = fields.Char()

    product_id = fields.Many2one('product.product',string=_("Product"))
    date = fields.Date(string=_("Date"),
                           default=lambda self: date.today(),
                           readonly=True)
    fin100_number = fields.Many2one('fw_pfb_fin_system_100',string=_("FIN100 ID")) 
    objective = fields.Text(string='Objective') 
    expense = fields.Char(string=_("Expense"))
    description = fields.Char(string=_("Description"))
    unit = fields.Float(string=_("Unit"))
    unit_name = fields.Many2one('uom.uom', string='Unit name')
    price_unit = fields.Float(string=_('Unit Price'), digits=dp.get_precision('Product Price'))
    amount = fields.Float(string=_('Amount'), digits=dp.get_precision('Product Price'))
    total = fields.Float(string=_('Total'), digits=dp.get_precision('Product Price'))
    status = fields.Char(string=_("Status"))
    fin_line_id = fields.Char(string='Fin line id' )
      
     
    wiz_id_all = fields.Many2one('fin_201_request_101_wiz',string=_("Purchase request"))   