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

class fin100_line_all_fin201_item(models.Model):
    _name = 'fin100_line_all_fin201_item'

    @api.one
    def _compute_total(self):
        for rec in self :
            line = self.env["fw_pfb_fin_system_201_line"].browse( int( rec.fin201_line_id ) )
            if line :
                if line.pay_amount :
                    rec.total = line.pay_amount

    '''
    fields
    '''
    wiz_id = fields.Many2one('fw_pfb_fin_system_100_line',string=_("Wizard request"))  

    fin_date = fields.Date(string='Fin Date')
    fin201_id = fields.Many2one('fw_pfb_fin_system_201', string=_("FIN201 Number"))
    fin201_line_id = fields.Char(string='FIN201 Line Number')
    product_id = fields.Many2one('product.product', string=_("Product"))
    description = fields.Char(string='Description' )
    status = fields.Char(string='FIN201 Status' )
    total = fields.Float('Total', compute='_compute_total')
    