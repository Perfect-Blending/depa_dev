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

class fw_pfb_related_deputy(models.Model):
    _name = 'fw_pfb_related_deputy'

    deputy_id = fields.Many2one('fw_pfb_fin_settings',string='Deputy')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    secretary  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Secretary')


class fw_pfb_related_assistant(models.Model):
    _name = 'fw_pfb_related_assistant'

    assistant_id = fields.Many2one('fw_pfb_fin_settings',string='Assistant')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    secretary  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Secretary')

class fw_pfb_related_director_secretary(models.Model):
    _name = 'fw_pfb_related_director_secretary'

    director_secretary_id = fields.Many2one('fw_pfb_fin_settings',string='Director Secretary')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_department(models.Model):
    _name = 'fw_pfb_related_department'

    department_id = fields.Many2one('fw_pfb_fin_settings',string='Department')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_financial_department(models.Model):
    _name = 'fw_pfb_related_financial_department'

    financial_department_id = fields.Many2one('fw_pfb_fin_settings',string='Financial Department')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_document_inspection1(models.Model):
    _name = 'fw_pfb_related_document_inspection1'

    document_inspection1_id = fields.Many2one('fw_pfb_fin_settings',string='Financial Department')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')

class fw_pfb_related_document_inspection2(models.Model):
    _name = 'fw_pfb_related_document_inspection2'

    document_inspection2_id = fields.Many2one('fw_pfb_fin_settings',string='Financial Department')
    
    name  = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Name')
    
    
    
