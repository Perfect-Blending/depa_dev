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
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

COPY_TEXT = "(copy)"

class fw_pfb_objective(models.Model):
    _name = 'fw_pfb_objective'

    

    name = fields.Char(string='Name', required=True )


    @api.multi
    def copy(self, default=None):
        copya = super(fw_pfb_objective, self).copy(default)
        if copya :
            copya.write({'name':copya.name + COPY_TEXT})
            
        return copya

