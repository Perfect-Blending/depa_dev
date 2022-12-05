# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
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

    director_of_department = fields.One2many(
        'fw_pfb_related_director_of_department',
        'related_id',
        default=_get_directorOfDepartment,
        string='Vice President Director'
    )

    directorOfOffice = fields.Many2one('hr.employee', 
                          default=_get_directorOfOffice,
                          required=True,
                          domain=[('fin_can_approve', '=', True)], 
                          string='President/CEO')
                  
    directorOfOffice_secretary  = fields.One2many(
        'fw_pfb_related_directorofoffice_secretary',
        'related_id',
        default=_get_directorOfOffice_secretary,
        string='Secretary'
    )
    deputyOfOffice  = fields.One2many(
        'fw_pfb_related_deputyofoffice',
        'related_id',
        default=_get_deputyOfOffice,
        string='Senior Executive Vice President',
    )
    assistantOfOffice  = fields.One2many(
        'fw_pfb_related_assistantofoffice',
        'related_id',
        default=_get_assistantOfOffice,
        string='Executive Vice President'
    )
    assistantOfOfficeManagement  = fields.One2many(
        'fw_pfb_related_assistantofofficemanagement',
        'related_id',
        default=_get_assistantOfOfficeManagement,
        string='Group Executive Vice President'
    )
    
    directorOfDirector  = fields.One2many(
        'fw_pfb_related_directorofdirector',
        'related_id',
        default=_get_directorOfDirector,
        string='Vice President of Agency Administration Department'
    )

    directorOfFinance  = fields.One2many(
        'fw_pfb_related_directoroffinance',
        'related_id',
        default=_get_directorOfFinance,
        string='Division Manager of Finance, Accounting and Control Division'
    )
    directorOfStrategy  = fields.One2many(
        'fw_pfb_related_directorofstrategy',
        'related_id',
        default=_get_directorOfStrategy,
        string='Vice President of Strategic Management Department'
    )
       
    directorOfEEC  = fields.One2many(
        'fw_pfb_related_directorofeec',
        'related_id',
        default=_get_directorOfEEC,
        string='director Of EEC'
    )
        
    budgetOwner  = fields.One2many(
        'fw_pfb_related_budgetowner',
        'related_id',
        default=_get_budgetOwner,
        string='Budget Owner'
    )
        
    ManagerOfStock  = fields.One2many(
        'fw_pfb_related_managerofstock',
        'related_id',
        default=_get_managerofstock,
        string='Division Manager of General Affairs and Facilities Division'
    )

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

        directorofoffice_secretary_ids = []
        if vals.get('directorOfOffice_secretary', False):
            for doos in vals['directorOfOffice_secretary']:
                if doos[2]:
                    if isinstance(doos[1], int):
                        directorofoffice_secretary_ids.append(doos[1])
            if directorofoffice_secretary_ids:
                directorofoffice_secretary_exclude_obj = self.env['fw_pfb_related_directorofoffice_secretary'].search([
                    ('id', 'not in', directorofoffice_secretary_ids)
                ])
                if directorofoffice_secretary_exclude_obj:
                    for doos_excl_obj in directorofoffice_secretary_exclude_obj:
                        doos_excl_obj.unlink()

        deputyofoffice_ids = []
        if vals.get('deputyOfOffice', False):
            for doo in vals['deputyOfOffice']:
                if doo[2]:
                    if isinstance(doo[1], int):
                        deputyofoffice_ids.append(doo[1])
            if deputyofoffice_ids:
                deputyofoffice_exclude_obj = self.env['fw_pfb_related_deputyofoffice'].search([
                    ('id', 'not in', deputyofoffice_ids)
                ])
                if deputyofoffice_exclude_obj:
                    for doo_excl_obj in deputyofoffice_exclude_obj:
                        doo_excl_obj.unlink()

        assistantofoffice_ids = []
        if vals.get('assistantOfOffice', False):
            for aoo in vals['assistantOfOffice']:
                if aoo[2]:
                    if isinstance(aoo[1], int):
                        assistantofoffice_ids.append(aoo[1])
            if assistantofoffice_ids:
                assistantofoffice_exclude_obj = self.env['fw_pfb_related_assistantofoffice'].search([
                    ('id', 'not in', assistantofoffice_ids)
                ])
                if assistantofoffice_exclude_obj:
                    for aoo_excl_obj in assistantofoffice_exclude_obj:
                        aoo_excl_obj.unlink()

        # assistantOfOfficeManagement
        assistantofofficemanagement_ids = []
        if vals.get('assistantOfOfficeManagement', False):
            for aom in vals['assistantOfOfficeManagement']:
                if aom[2]:
                    if isinstance(aom[1], int):
                        assistantofofficemanagement_ids.append(aom[1])
            if assistantofofficemanagement_ids:
                assistantofofficemanagement_exclude_obj = self.env['fw_pfb_related_assistantofofficemanagement'].search([
                    ('id', 'not in', assistantofofficemanagement_ids)
                ])
                if assistantofofficemanagement_exclude_obj:
                    for aom_excl_obj in assistantofofficemanagement_exclude_obj:
                        aom_excl_obj.unlink()

        # directorOfDirector
        directorofdirector_ids = []
        if vals.get('directorOfDirector', False):
            for dod in vals['directorOfDirector']:
                if dod[2]:
                    if isinstance(dod[1], int):
                        directorofdirector_ids.append(dod[1])
            if directorofdirector_ids:
                directorofdirector_exclude_obj = self.env['fw_pfb_related_directorofdirector'].search(
                    [
                        ('id', 'not in', directorofdirector_ids)
                    ])
                if directorofdirector_exclude_obj:
                    for dod_excl_obj in directorofdirector_exclude_obj:
                        dod_excl_obj.unlink()

        # directorOfFinance
        directoroffinance_ids = []
        if vals.get('directorOfFinance', False):
            for dof in vals['directorOfFinance']:
                if dof[2]:
                    if isinstance(dof[1], int):
                        directoroffinance_ids.append(dof[1])
            if directoroffinance_ids:
                directoroffinance_exclude_obj = self.env['fw_pfb_related_directoroffinance'].search(
                    [
                        ('id', 'not in', directoroffinance_ids)
                    ])
                if directoroffinance_exclude_obj:
                    for dof_excl_obj in directoroffinance_exclude_obj:
                        dof_excl_obj.unlink()

        # directorOfStrategy
        directorofstrategy_ids = []
        if vals.get('directorOfStrategy', False):
            for dos in vals['directorOfStrategy']:
                if dos[2]:
                    if isinstance(dos[1], int):
                        directorofstrategy_ids.append(dos[1])
            if directorofstrategy_ids:
                directorofstrategy_exclude_obj = self.env['fw_pfb_related_directorofstrategy'].search(
                    [
                        ('id', 'not in', directorofstrategy_ids)
                    ])
                if directorofstrategy_exclude_obj:
                    for dos_excl_obj in directorofstrategy_exclude_obj:
                        dos_excl_obj.unlink()

        # directorOfEEC
        directorofeec_ids = []
        if vals.get('directorOfEEC', False):
            for doe in vals['directorOfEEC']:
                if doe[2]:
                    if isinstance(doe[1], int):
                        directorofeec_ids.append(doe[1])
            if directorofeec_ids:
                directorofeec_exclude_obj = self.env['fw_pfb_related_directorofeec'].search(
                    [
                        ('id', 'not in', directorofeec_ids)
                    ])
                if directorofeec_exclude_obj:
                    for doe_excl_obj in directorofeec_exclude_obj:
                        doe_excl_obj.unlink()

        # budgetOwner
        budgetowner_ids = []
        if vals.get('budgetOwner', False):
            for bo in vals['budgetOwner']:
                if bo[2]:
                    if isinstance(bo[1], int):
                        budgetowner_ids.append(bo[1])
            if budgetowner_ids:
                budgetowner_exclude_obj = self.env['fw_pfb_related_budgetowner'].search(
                    [
                        ('id', 'not in', budgetowner_ids)
                    ])
                if budgetowner_exclude_obj:
                    for bo_excl_obj in budgetowner_exclude_obj:
                        bo_excl_obj.unlink()

        # ManagerOfStock
        managerofstock_ids = []
        if vals.get('ManagerOfStock', False):
            for mos in vals['ManagerOfStock']:
                if mos[2]:
                    if isinstance(mos[1], int):
                        managerofstock_ids.append(mos[1])
            if managerofstock_ids:
                managerofstock_exclude_obj = self.env['fw_pfb_related_managerofstock'].search(
                    [
                        ('id', 'not in', managerofstock_ids)
                    ])
                if managerofstock_exclude_obj:
                    for mos_excl_obj in managerofstock_exclude_obj:
                        mos_excl_obj.unlink()

        # director_of_department
        director_of_department_ids = []
        if vals.get('director_of_department', False):
            for dod in vals['director_of_department']:
                if dod[2]:
                    if isinstance(dod[1], int):
                        director_of_department_ids.append(dod[1])
            if director_of_department_ids:
                director_of_department_exclude_obj = self.env['fw_pfb_related_director_of_department'].search(
                    [
                        ('id', 'not in', director_of_department_ids)
                    ])
                if director_of_department_exclude_obj:
                    for dod_excl_obj in director_of_department_exclude_obj:
                        dod_excl_obj.unlink()

        res = super(fw_pfb_fin_settings2, self).write(vals)
        return res

    @api.multi    
    def apply(self):
       
        return {
          'type': 'ir.actions.client',
          'tag': 'reload',
        }  


        
    

    
    
    
    