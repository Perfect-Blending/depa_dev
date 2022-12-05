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

FIN_TYPE_SELECTION = [('eroe', 'Expense request of express'),
                   ('erob', 'Expense request of budget'),
                   ('proo', 'Purchase reguest of objective'),
                   ('pors', 'Purchase request of stock'),
                   ('lr', 'Loan request'),
                   ('parr', 'Payment and refund request')]

APPROVE_POSITION = [('DirectorOfDepartment', 'Vice President/Director'),
                    ('RelatedGroup', 'Related Group'),
                    ('DirectorOfFinance', 'Division Manager of Finance, Accounting and Control Division'),
                    ('ManagerOfStock', 'Division Manager of General Affairs and Facilities Division'),
                    ('AssistantOfOffice', 'Executive Vice President'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),
                    ('SmallNote', 'Small Note'),
                    ('DirectorOfOffice', 'President/CEO')]

POSITION_INDEX = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),
                  (11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20)]

POSITION = [('DirectorOfDepartment', 'Vice President Director'),
                    ('DirectorOfEEC', 'Director Of EEC'),
                    ('DirectorOfStrategy', 'Vice President of Strategic Management Department'),
                    ('BudgetOwner', 'Budget Owner'),
                    ('DirectorOfFinance', 'Vice President of Finance and General Affairs Department'),
                    ('ManagerOfStock', 'Division Manager of General Affairs and Facilities Division'),
                    ('AssistantOfOffice', 'Executive Vice President'),('AssistantOfOfficeSecretary', 'Assistant Team Leader'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),('DeputyOfOfficeSecretary', 'Deputy Team Leader'),
                    ('AssistantOfOfficeManagement', 'Group Executive Vice President'),
                    ('DirectorOfDirector', 'Vice President of Agency Administration Department'),
                    ('DirectorOfOffice', 'President/CEO'), ('DirectorOfOfficeSecretary', 'Senior Team Leader')]

class fw_pfb_flow_template(models.Model):
    _name = 'fw_pfb_flow_template'

    @api.multi
    def generate_index(self):
      if self.id :
        count = 0
        if self.approve_line :
          count = len( self.approve_line ) + 1
          for ap in self.approve_line :
            if ap.id :
              count = count - 1
              apid = self.env['fw_pfb_flow_template_approve'].browse( ap.id )
              apid.write({"position_index" : int(count) })

    name = fields.Char(string='Name', required=True )
    department = fields.Many2one('hr.department',
                                 string='Department', 
                                 required=True)

    type = fields.Selection(FIN_TYPE_SELECTION, string='Fin Type')
    data_activate = fields.Boolean(string='Active', default=True)

    approve_line = fields.One2many('fw_pfb_flow_template_approve',
                                'approve_id',
                                copy=True )


class fw_pfb_flow_template_approve(models.Model):
    _name = 'fw_pfb_flow_template_approve'
    _order = 'position_index asc'

    @api.multi
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

    @api.multi
    def _get_directorOfOffice_secretary(self):
        list = False
        datas = self.env['fw_pfb_related_directorofoffice_secretary'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_deputyOfOffice(self):
        list = False
        datas = self.env['fw_pfb_related_deputyofoffice'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_assistantOfOffice(self):
        list = False
        datas = self.env['fw_pfb_related_assistantofoffice'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_assistantOfOfficeManagement(self):
        list = False
        datas = self.env['fw_pfb_related_assistantofofficemanagement'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_directorOfDirector(self):
        list = False
        datas = self.env['fw_pfb_related_directorofdirector'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list   

    @api.multi
    def _get_directorOfFinance(self):
        list = False
        datas = self.env['fw_pfb_related_directoroffinance'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_directorOfStrategy(self):
        list = False
        datas = self.env['fw_pfb_related_directorofstrategy'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_directorOfEEC(self):
        list = False
        datas = self.env['fw_pfb_related_directorofeec'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_budgetOwner(self):
        list = False
        datas = self.env['fw_pfb_related_budgetowner'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list 

    @api.multi
    def _get_managerofstock(self):
        list = False
        datas = self.env['fw_pfb_related_managerofstock'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.multi
    def _get_directorOfDepartment(self):
        list = False
        datas = self.env['fw_pfb_related_director_of_department'].search([])
        if datas :
          list = datas
        else :
          list = []

        return list

    @api.onchange('position')
    def _onchange_position(self):
        list = False
        self.employee_line = False
        self.emp_name = False

        if self.position == "DirectorOfDepartment" :
          list = self._get_directorOfDepartment()
        elif self.position == "DirectorOfEEC" :
          list = self._get_directorOfEEC()
        elif self.position == "DirectorOfStrategy" :
          list = self._get_directorOfStrategy()
        elif self.position == "BudgetOwner" :
          list = self._get_budgetOwner()
        elif self.position == "DirectorOfFinance" :
          list = self._get_directorOfFinance()
        elif self.position == "ManagerOfStock" :
          list = self._get_managerofstock()
        elif self.position == "AssistantOfOffice" :
          list = self._get_assistantOfOffice()
        elif self.position == "AssistantOfOfficeSecretary" :
          list = self._get_assistantOfOffice()
        elif self.position == "DeputyOfOffice" :
          list = self._get_deputyOfOffice()
        elif self.position == "DeputyOfOfficeSecretary" :
          list = self._get_deputyOfOffice()
        elif self.position == "AssistantOfOfficeManagement" :
          list = self._get_assistantOfOfficeManagement()
        elif self.position == "DirectorOfDirector" :
          list = self._get_directorOfDirector()
        elif self.position == "DirectorOfOffice" :
          list = self._get_directorOfOffice()
        elif self.position == "DirectorOfOfficeSecretary" :
          list = self._get_directorOfOffice_secretary()

        if self.position != "AssistantOfOfficeSecretary" and self.position != "DeputyOfOfficeSecretary" and self.position != "DirectorOfOffice" :
            if list :
              for i in list :
                self.employee_line += self.employee_line.new({"name" : i.name.id })
        elif self.position == "DirectorOfOffice" :
            if list :
              self.employee_line += self.employee_line.new({"name" : list })
        else :
          if list :
              for i in list :
                self.employee_line += self.employee_line.new({"name" : i.secretary.id })

    approve_id = fields.Many2one('fw_pfb_flow_template',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)

    @api.onchange('employee_line')
    def _onchange_employee_line(self):
        counter = 0
        self.emp_name = False
        if self.employee_line :
          for i in self.employee_line :
            if i.data_activate :
              counter = counter + 1

        if self.position :
          if counter > 1 :
              raise UserError(_("Please select employee only once."))
          else :
            for i in self.employee_line :
              if i.data_activate :
                self.emp_name = i.name.id

    position_index = fields.Selection(POSITION_INDEX, string='Approve Index')
    approve_position = fields.Selection(APPROVE_POSITION, string='Approve Position', required=True)
    position = fields.Selection(POSITION, string='Position', required=True)
    emp_name = fields.Many2one('hr.employee', domain=[('fin_can_approve', '=', True)], required=True, string='Employee Name')
    data_activate = fields.Boolean(string='Active')

    employee_line = fields.One2many('fw_pfb_flow_template_employee_list', 'release_id' )      


class fw_pfb_flow_template_employee_list(models.TransientModel):
    _name = 'fw_pfb_flow_template_employee_list'

    release_id = fields.Many2one('fw_pfb_flow_template_approve')

    data_activate = fields.Boolean(string='Active')
    name = fields.Many2one('hr.employee', string='Employee Name')
    

