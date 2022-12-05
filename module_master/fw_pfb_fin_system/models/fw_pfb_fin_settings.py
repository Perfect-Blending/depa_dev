# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from datetime import datetime, timedelta
from openerp.exceptions import UserError
from lxml import etree
import logging
from openerp.osv import orm
_logger = logging.getLogger(__name__)



class fw_pfb_fin_settings(models.Model):
    _name = 'fw_pfb_fin_settings'
    
    def _get_director(self):
      sid = False
      hasSettings = self.env['fw_pfb_fin_settings'].search([], limit=1)
      if hasSettings :
        for i in hasSettings :
          fin = self.env['fw_pfb_fin_settings'].browse( i.id )
          if fin :
            if fin.director :
              sid = fin.director.id
      return sid

    def _get_related_department(self):
        list = False
        datas = self.env['fw_pfb_related_department'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_financial_department(self):
        list = False
        datas = self.env['fw_pfb_related_financial_department'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list
        
    def _get_document_inspection1(self):
        list = False
        datas = self.env['fw_pfb_related_document_inspection1'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_document_inspection2(self):
        list = False
        datas = self.env['fw_pfb_related_document_inspection2'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_deputy_ids(self):
        list = False
        datas = self.env['fw_pfb_related_deputy'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list
        
    def _get_assistant_ids(self):
        list = False
        datas = self.env['fw_pfb_related_assistant'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    def _get_director_secretary(self):
        list = False
        datas = self.env['fw_pfb_related_director_secretary'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list


    director = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], default=_get_director, string='Name')
    director_secretary  = fields.One2many('fw_pfb_related_director_secretary','director_secretary_id', 
                          default=_get_director_secretary, 
                          string='Secretary')

    deputy_ids = fields.One2many('fw_pfb_related_deputy','deputy_id' , 
                  default=_get_deputy_ids ,
                  string='Deputy ids')

    assistant_ids = fields.One2many('fw_pfb_related_assistant','assistant_id', 
                      default=_get_assistant_ids ,
                      string='Assistant ids')

    related_department = fields.One2many('fw_pfb_related_department','department_id', 
                    default=_get_related_department,
                    string='Related Group')

    financial_department = fields.One2many('fw_pfb_related_financial_department','financial_department_id', 
                          default=_get_financial_department, 
                          string='Financial Department')

    document_inspection1 = fields.One2many('fw_pfb_related_document_inspection1','document_inspection1_id', 
                          default=_get_document_inspection1, 
                          string='Document Inspection')

    document_inspection2 = fields.One2many('fw_pfb_related_document_inspection2','document_inspection2_id', 
                          default=_get_document_inspection2, 
                          string='Document Inspection')

    @api.model
    def create(self, vals):
        
        fin_id = False
        hasSettings = self.env['fw_pfb_fin_settings'].search([], limit=1)
        if not hasSettings :
          fin_id = super(fw_pfb_fin_settings, self).create(vals)
        else :
          for i in hasSettings :
            fin_id = i
            fin_id.write( vals )


        return fin_id
    
    @api.multi
    def write(self, vals):
        return super(fw_pfb_fin_settings, self).write(vals)

    @api.multi    
    def apply(self):
       
        return {
          'type': 'ir.actions.client',
          'tag': 'reload',
        }  


        
    

    
    
    
    