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
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import datetime
# translation
finish_choose_NO_SELECT = _("Please choose at least a item to import to PO")

STATE_SELECTION = [('apply',_('Apply filter')),
                    ('reset',_('Reset filter')),
                    ('all',_('Select all items')),
                    ('clear',_('Deselect all items')),
                    ]
                    
FIN_TYPE_PULL_FIN100 = [('eroe', 'Expense request of express'),
                   ('erob', 'Expense request of budget'),
                   ('proo', 'Purchase reguest of objective')]


class fin_100_request_wiz(models.TransientModel):
    _name = 'fin_100_request_wiz'
      
    '''
    fields
    '''
    item_fin100_ids = fields.One2many('fin_100_request_wiz_item','wiz_id',string=_('Request items'))  
    item_fin100_ids_all = fields.One2many('fin_100_request_wiz_item','wiz_id_all',string=_('Request items'))  


    filter_fin_type = fields.Selection(FIN_TYPE_PULL_FIN100, string='FIN Type')
    filter_product_can_be_expensed = fields.Many2one('product.template',string=_("Product Can be expensed"),domain=[('fin_ok', '=', True)])
    filter_product = fields.Char('Product')
    filter_code = fields.Char('Code')
    filter_prall = fields.Boolean('All FIN100')
    filter_fin100_number = fields.Many2one('fw_pfb_fin_system_100',string=_("FIN100 Number"))
    filter_action = fields.Selection( STATE_SELECTION ,string=_("Filter action"))

    # To filter can_cross_department from FIN100
    filter_cross_department = fields.Boolean(
        string='Cross Department'
    )

    @api.onchange('filter_fin_type',
                  'filter_product_can_be_expensed',
                  'filter_product',
                  'filter_code',
                  'filter_prall',
                  'filter_fin100_number',
                  'filter_cross_department')
    def _check_auto_filter(self):
        print('AUTO FILTTER---- 201')
        current_user = self._context.get('uid')
        if current_user:
            user_obj = self.env['res.users'].search([
                ('id', '=', current_user),
            ])
            if user_obj:
                if user_obj.has_group('fin_system.fw_pfb_fin_system_auto_fin_100'):
                    self.item_fin100_ids = None
                    self.item_fin100_ids_all = None
                    self.filter_action = self.filter_action or 'apply'
                    self.do_action()


    @api.multi
    def load_fin100(self, fin_all):
        rules = []
        plist = []

        current_user = self._context.get('uid')

        user = False
        department_id = False
        if current_user:
            user = self.env['hr.employee'].search([('user_id', '=', current_user)], limit=1)
            if user :
                if self.filter_cross_department:
                    rules.append(('can_cross_department', '=', True))
                else:
                    if user.department_id :
                        department_id = user.department_id.id
            
        
        if self.filter_product :
            pro = self.env['product.product'].search([('name','like', self.filter_product)])
            if pro :
                for p in pro :
                    plist.append( p.id )

        rules.append( ('state','=','completed') )
        if self.filter_fin100_number :
            rules.append( ('id','=',self.filter_fin100_number.id) )

        #if user :
            #rules.append( ('requester','=',user.id ) )

        if self.filter_fin_type :
            rules.append( ('fin_type','=', self.filter_fin_type ) )

        # Append only fin is open
        rules.append( ('is_fin_open', '=', True) )
        print( rules )
        

        self.item_fin100_ids = False
        fins = self.env['fw_pfb_fin_system_100'].search(rules)

        if fins :
            for fin in fins :
                canAddFin = True
                if department_id :
                    if fin.requester :
                        if fin.requester.department_id :
                            if department_id != fin.requester.department_id.id :
                                canAddFin = False
                        else :
                            canAddFin = False
                
                if canAddFin :
                    rules = []
                    rules.append( ('fin_id','=',fin.id) )
                    if self.filter_product_can_be_expensed :
                        ptempl = self.env['product.product'].search([('product_tmpl_id','=',self.filter_product_can_be_expensed.id)],limit=1)
                        if ptempl :
                            rules.append( ('product_id','=',ptempl.id) )
                    if self.filter_product :
                        if len( plist ) > 0 :
                            rules.append( ('product_id','in', plist) )
                    print( rules )
                    lines = self.env['fw_pfb_fin_system_100_line'].search(rules)
                    if lines :
                        for line in lines :
                            if self.filter_code :
                                if line.product_id :
                                    product = self.env['product.product'].search([('id','=',line.product_id.id)])
                                    if product :
                                        if product.default_code :
                                            if str(product.default_code) == str(self.filter_code) :
                                                if fin_all :
                                                    self.add_fin100_all( fin, line )
                                                else :
                                                    self.add_fin100( fin, line )
                            else :   
                                if fin_all :
                                    self.add_fin100_all( fin, line )
                                else :
                                    self.add_fin100( fin, line )

    @api.multi
    def add_fin100(self, fin, line):
        finline = self.env['fw_pfb_fin_system_401_line'].search([('fin_line_id','=', str(line.id) )] )
        can_push = True
        '''if not finline :
            can_push = True
        else :
            for i in finline :
                if i.fin_id :
                    fin401 = self.env['fw_pfb_fin_system_401'].search([ ('id','=', str( i.fin_id.id ) ), ('state', 'in', ['cancelled']) ] )
                    if fin401 :
                        can_push = True
                    else :
                        can_push = False'''


        
        if can_push :
            data = {
                    "date" : fin.fin_date,
                    "fin100_number" : fin.id,
                    "fin_type" : fin.fin_type,
                    "expense" : line.product_id.name,
                    "description" : line.description,
                    "unit" : line.product_uom_qty,
                    "unit_name" : line.product_uom.id,
                    "price_unit" : line.price_unit,
                    "amount" : line.product_uom_qty * line.price_unit,
                    "total" : 0,
                    "status" : fin.state,
                    "product_id" : line.product_id.id,
                    "fin_line_id" :  str(line.id)
                }
            print(data)
            self.item_fin100_ids += self.item_fin100_ids.create( data )

    @api.multi
    def add_fin100_all(self, fin, line):
        finline = self.env['fw_pfb_fin_system_401_line'].search([('fin_line_id','=', str(line.id) )] )
        
        can_push = True
        '''if finline :
            can_push = True
        else :
            for i in finline :
                if i.fin_id :
                    fin401 = self.env['fw_pfb_fin_system_401'].search([ ('id','=', str( i.fin_id.id ) ), ('state', 'in', ['cancelled']) ] )
                    if fin401 :
                        can_push = True
                    else :
                        can_push = False'''

        if can_push :
            data = {
                "date" : fin.fin_date,
                "fin100_number" : fin.id,
                "fin_type" : fin.fin_type,
                "expense" : line.product_id.name,
                "description" : line.description,
                "unit" : line.product_uom_qty,
                "unit_name" : line.product_uom.id,
                "price_unit" : line.price_unit,
                "amount" : line.product_uom_qty * line.price_unit,
                "total" : 0,
                "status" : fin.state,
                "product_id" : line.product_id.id,
                "fin_line_id" :  str(line.id)
            }
            print(data)
            self.item_fin100_ids_all += self.item_fin100_ids_all.create( data )


    @api.onchange('filter_action')
    def do_action(self):
        # apply all filter, reload all data
        if self.filter_action == 'apply':
            if self.filter_prall:
                self.load_fin100( True )
            else :
                self.load_fin100( False )

        elif self.filter_action == 'reset':
            self.filter_product_can_be_expensed = False
            self.filter_product = False
            self.filter_code = False
            self.filter_prall = False
            self.filter_fin100_number = False
            self.filter_code = False

            self.item_fin100_ids = False
            self.item_fin100_ids_all = False
            
        elif self.filter_action == 'all':
            for each in self.item_fin100_ids:
                each.select = True
        elif self.filter_action == 'clear':
            for each in self.item_fin100_ids:
                each.select = False
        
        # reset action
        self.filter_action = False
        return

    @api.multi
    def finish_choose(self):
        fin401_id = False
        if 'active_id' in self._context :
            fin401_id = self._context['active_id']
        elif 'id' in self._context['params'] :
            fin401_id = self._context['params']['id']

        list = False
        all = False
        if self.filter_prall:
            list = self.item_fin100_ids_all
            all = True
        else :
            list = self.item_fin100_ids
        
        if list :
            env = self.env['fw_pfb_fin_system_401_line']

            cloneDatas = False

            objective = False
            fin_objective = False
            other = False
            estimate_output = False
            participantas_quantity = False

            f401 = self.env['fw_pfb_fin_system_401'].browse( fin401_id )

            for each in list :
                if each.select or all:
                    if not cloneDatas :
                        cloneDatas = True

                        objective = each.fin100_number.objective
                        if each.fin100_number.fin_objective :
                            fin_objective = each.fin100_number.fin_objective.id
                        other = each.fin100_number.other
                        estimate_output = each.fin100_number.estimate_output
                        participantas_quantity = each.fin100_number.participantas_quantity

                        if f401 :
                            f401.write({"objective" : objective,
                                "fin_objective" : fin_objective,
                                "other" : other,
                                "estimate_output" : estimate_output,
                                "participantas_quantity" : participantas_quantity,
                            })


                    data = {
                        "fin_id" : fin401_id,
                        "description" : each.description,
                        "product_uom" : each.unit_name.id,
                        "product_uom_qty" : each.unit,
                        "price_unit" : each.price_unit,
                        "price_subtotal" : each.unit * each.price_unit,
                        "product_id" : each.product_id.id,
                        # "projects_and_plan" : False,
                        "fin_line_id" : str(each.fin_line_id),
                        "fin100_id" : each.fin100_number.id,
                        "fin100_line_id": self.env['fw_pfb_fin_system_100_line'].browse(int(each.fin_line_id)).id,
                        "fin_type" : each.fin_type,
                    }
                    lid = env.create(data)

                    fin100_line_id = self.env['fw_pfb_fin_system_100_line'].browse( int( each.fin_line_id ) )
                    if fin100_line_id :
                        data2 = {
                            "wiz_id" : each.fin_line_id,
                            "fin_date" : each.date,
                            "fin401_id" : str(fin401_id),
                            "fin401_line_id" : lid.id,
                            "product_id" : each.product_id.id,
                            "description" : each.description,
                            "status" : "draft"
                        }
                        print(data2)
                        fin100_line_id.item_fin401_ids.create(data2)

                        
                        if f401 :
                            f401.write({"swap" : True})
                    

    # @api.one
    # @api.onchange('filter_prall')
    # def change_filter_prall(self):
    #     if self.filter_prall:
    #         self.filter_product_can_be_expensed = False
    #         self.filter_product = False
    #         self.filter_code = False
                                        
      
      
      