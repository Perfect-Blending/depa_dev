# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    sale_edit_sequence = fields.Boolean("Sale Edit Sequence ?",default=False,compute ='sale_edit_sequence_number_group')
    
    @api.one
    @api.depends('name')
    def sale_edit_sequence_number_group(self):
        
        if self and self.name:
            
            if self.name == 'New':
                self.sale_edit_sequence = False 
            
            else :  
                if self.user_has_groups('sh_edit_sequence_no.group_sale_order_edit_sequence'): 
                    self.sale_edit_sequence = True
                else:        
                    self.sale_edit_sequence = False 
                    
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    purchase_edit_sequence = fields.Boolean("Purchase Edit Sequence ?",default=False,compute ='purchase_edit_sequence_number_group')
    
    @api.one
    @api.depends('name')
    def purchase_edit_sequence_number_group(self):
        
        if self and self.name:
            
            if self.name == 'New':
                self.purchase_edit_sequence = False 
            
            else :  
                if self.user_has_groups('sh_edit_sequence_no.group_purchase_order_edit_sequence'): 
                    self.purchase_edit_sequence = True
                else:        
                    self.purchase_edit_sequence = False
                    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    account_edit_sequence = fields.Boolean("Account Edit Sequence ?",default=False,compute ='account_edit_sequence_number_group')
    
    @api.one
    @api.depends('number')
    def account_edit_sequence_number_group(self):

        if self:

            if self.number == False:
                self.account_edit_sequence = False 
            
            else :  
                if self.user_has_groups('sh_edit_sequence_no.group_account_invoice_edit_sequence'): 
                    self.account_edit_sequence = True
                else:        
                    self.account_edit_sequence = False 
                    

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    stock_picking_edit_sequence = fields.Boolean("Stock Edit Sequence ?",default=False,compute ='stock_edit_sequence_number_group')
    
    @api.one
    @api.depends('name')
    def stock_edit_sequence_number_group(self):
        
        if self and self.name:

            if self.name == '/':
                self.stock_picking_edit_sequence = False 
            
            else :  
                if self.user_has_groups('sh_edit_sequence_no.group_stock_edit_sequence'): 
                    self.stock_picking_edit_sequence = True
                else:        
                    self.stock_picking_edit_sequence = False 
                                         
