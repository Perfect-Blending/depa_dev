# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from datetime import datetime, timedelta
from openerp.exceptions import UserError
from lxml import etree
import logging
from openerp.osv import orm
_logger = logging.getLogger(__name__)



class fw_pfb_fin_settings2(models.Model):
    _name = 'fw_pfb_fin_settings2'
    
    def _get_directorOfOffice(self):
        sid = False
        hasSettings = self.env['fw_pfb_fin_settings2'].search([], limit=1)
        if hasSettings :
          for i in hasSettings :
            fin = self.env['fw_pfb_fin_settings2'].browse( i.id )
            if fin :
              if fin.directorOfOffice :
                sid = fin.directorOfOffice.id
        return sid

    def _get_directorOfOffice_secretary(self):
        list = False
        datas = self.env['fw_pfb_related_directorofoffice_secretary'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_deputyOfOffice(self):
        list = False
        datas = self.env['fw_pfb_related_deputyofoffice'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_assistantOfOffice(self):
        list = False
        datas = self.env['fw_pfb_related_assistantofoffice'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_assistantOfOfficeManagement(self):
        list = False
        datas = self.env['fw_pfb_related_assistantofofficemanagement'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_directorOfDirector(self):
        list = False
        datas = self.env['fw_pfb_related_directorofdirector'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list   

    def _get_directorOfFinance(self):
        list = False
        datas = self.env['fw_pfb_related_directoroffinance'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_directorOfStrategy(self):
        list = False
        datas = self.env['fw_pfb_related_directorofstrategy'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_directorOfEEC(self):
        list = False
        datas = self.env['fw_pfb_related_directorofeec'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_budgetOwner(self):
        list = False
        datas = self.env['fw_pfb_related_budgetowner'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list 

    def _get_managerofstock(self):
        list = False
        datas = self.env['fw_pfb_related_managerofstock'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_directorOfDepartment(self):
        list = False
        datas = self.env['fw_pfb_related_director_of_department'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    director_of_department = fields.One2many('fw_pfb_related_director_of_department',
                          'related_id',
                          default=_get_directorOfDepartment,
                          string='Vice President Director')

    directorOfOffice = fields.Many2one('hr.employee', 
                          default=_get_directorOfOffice,
                          required=True,
                          domain=[('fin_can_approve', '=', True)], 
                          string='President/CEO')
                  
    directorOfOffice_secretary  = fields.One2many('fw_pfb_related_directorofoffice_secretary',
                          'related_id', 
                          default=_get_directorOfOffice_secretary,
                          string='Secretary')


    deputyOfOffice  = fields.One2many(
        'fw_pfb_related_deputyofoffice',
        'related_id',
        default=_get_deputyOfOffice,
        string='Senior Executive Vice President',
    )
    assistantOfOffice  = fields.One2many('fw_pfb_related_assistantofoffice',
                          'related_id', 
                          default=_get_assistantOfOffice,
                          string='Executive Vice President')
    assistantOfOfficeManagement  = fields.One2many('fw_pfb_related_assistantofofficemanagement',
                          'related_id', 
                          default=_get_assistantOfOfficeManagement,
                          string='Group Executive Vice President')
    
    directorOfDirector  = fields.One2many('fw_pfb_related_directorofdirector',
                          'related_id',
                          default=_get_directorOfDirector,
                          string='Vice President of Agency Administration Department')

    directorOfFinance  = fields.One2many('fw_pfb_related_directoroffinance',
                          'related_id', 
                          default=_get_directorOfFinance,
                          string='Division Manager of Finance, Accounting and Control Division')
    directorOfStrategy  = fields.One2many('fw_pfb_related_directorofstrategy',
                          'related_id', 
                          default=_get_directorOfStrategy,
                          string='Vice President of Strategic Management Department')
       
    directorOfEEC  = fields.One2many('fw_pfb_related_directorofeec',
                          'related_id', 
                          default=_get_directorOfEEC,
                          string='director Of EEC')
        
    budgetOwner  = fields.One2many('fw_pfb_related_budgetowner',
                          'related_id', 
                          default=_get_budgetOwner,
                          string='Budget Owner')
        
    ManagerOfStock  = fields.One2many('fw_pfb_related_managerofstock',
                          'related_id', 
                          default=_get_managerofstock,
                          string='Division Manager of General Affairs and Facilities Division')

    @api.model
    def create(self, vals):
        
        fin_id = False
        hasSettings = self.env['fw_pfb_fin_settings2'].search([], limit=1)
        if not hasSettings :
          fin_id = super(fw_pfb_fin_settings2, self).create(vals)
        else :
          for i in hasSettings :
            fin_id = i
            fin_id.write( vals )


        return fin_id
    
    @api.multi
    def write(self, vals):
        return super(fw_pfb_fin_settings2, self).write(vals)

    @api.multi    
    def apply(self):
       
        return {
          'type': 'ir.actions.client',
          'tag': 'reload',
        }  


        
    

    
    
    
    