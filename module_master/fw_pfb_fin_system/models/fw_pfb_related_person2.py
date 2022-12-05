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

class fw_pfb_related_directorofoffice_secretary(models.Model):
    _name = 'fw_pfb_related_directorofoffice_secretary'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_deputyofoffice(models.Model):
    _name = 'fw_pfb_related_deputyofoffice'

    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    secretary  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Secretary')
   
class fw_pfb_related_assistantofoffice(models.Model):
    _name = 'fw_pfb_related_assistantofoffice'

    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    secretary  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Secretary')
   
class fw_pfb_related_assistantofofficemanagement(models.Model):
    _name = 'fw_pfb_related_assistantofofficemanagement'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
   
class fw_pfb_related_directorofdirector(models.Model):
    _name = 'fw_pfb_related_directorofdirector'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

       
class fw_pfb_related_directoroffinance(models.Model):
    _name = 'fw_pfb_related_directoroffinance'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

       
class fw_pfb_related_directorofstrategy(models.Model):
    _name = 'fw_pfb_related_directorofstrategy'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

       
class fw_pfb_related_directorofeec(models.Model):
    _name = 'fw_pfb_related_directorofeec'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    

       
class fw_pfb_related_budgetowner(models.Model):
    _name = 'fw_pfb_related_budgetowner'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_managerofstock(models.Model):
    _name = 'fw_pfb_related_managerofstock'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_director_of_department(models.Model):
    _name = 'fw_pfb_related_director_of_department'
    
    related_id = fields.Many2one('fw_pfb_fin_settings2',string='Related')
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    