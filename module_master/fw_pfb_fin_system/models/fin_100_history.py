# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from datetime import datetime
from openerp.exceptions import UserError
from lxml import etree
import logging
from openerp.osv import orm
_logger = logging.getLogger(__name__)


POSITION_INDEX = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),
                  (11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20)]

PRIORITY = [('1_normal', 'Normal'),
                   ('0_urgent', 'Urgent')]
                  
POSITION_CLASS = {
    "DirectorOfDepartment" : "fw_pfb_related_director_of_department",
    "DirectorOfEEC" : "fw_pfb_related_directorofeec",
    "DirectorOfStrategy" : "fw_pfb_related_directorofstrategy",
    "BudgetOwner" : "fw_pfb_related_budgetowner",
    "DirectorOfFinance" : "fw_pfb_related_directoroffinance",
    "ManagerOfStock" : "fw_pfb_related_managerofstock",
    "AssistantOfOffice" : "fw_pfb_related_assistantofoffice",
    "AssistantOfOfficeSecretary" : "fw_pfb_related_assistantofoffice",
    "DeputyOfOffice" : "fw_pfb_related_deputyofoffice",
    "DeputyOfOfficeSecretary" : "fw_pfb_related_deputyofoffice",
    "AssistantOfOfficeManagement" : "fw_pfb_related_assistantofofficemanagement",
    "DirectorOfDirector" : "fw_pfb_related_directorofdirector",
    "DirectorOfOfficeSecretary" : "fw_pfb_related_directorofoffice_secretary",
}

STATE_SELECTION = [ ('draft', 'Draft'),
                    ('sent', 'Sent'),
                    ('DirectorOfDepartment', 'Vice President/Director'),
                    ('RelatedGroup', 'Related Group'),
                    ('DirectorOfFinance', 'Division Manager of Finance, Accounting and Control Division'),
                    ('AssistantOfOffice', 'Executive Vice President'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),
                    ('SmallNote', 'Small Note'),
                    ('DirectorOfOffice', 'Director'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                    ('reject', 'Reject')]

OLD_FIN_SELECTION = [('project_head_preliminary_supervisor', 'Project head/Preliminary Supervisor'),
                 ('related_department', 'Related Group'),
                 ('deputy_director', 'Deputy Director'),
                 ('director', 'Director')]

APPROVE_POSITION = [('DirectorOfDepartment', 'Vice President/Director'),
                    ('RelatedGroup', 'Related Group'),
                    ('DirectorOfFinance', 'Division Manager of Finance, Accounting and Control Division'),
                    ('ManagerOfStock', 'Division Manager of General Affairs and Facilities Division'),
                    ('AssistantOfOffice', 'Executive Vice President'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),
                    ('SmallNote', 'Small Note'),
                    ('DirectorOfOffice', 'President/CEO')]


FIN_SELECTION = [('DirectorOfDepartment', 'Vice President Director'),
                    ('DirectorOfEEC', 'Director Of EEC'),
                    ('DirectorOfStrategy', 'Vice President of Strategic Management Department'),
                    ('BudgetOwner', 'Budget Owner'),
                    ('DirectorOfFinance', 'Vice President of Finance and General Affairs Department'),
                    ('ManagerOfStock', 'Division Manager of General Affairs and Facilities Division'),
                    ('AssistantOfOffice', 'Executive Vice President'),
                    ('AssistantOfOfficeSecretary', 'Assistant Team Leader'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),
                    ('DeputyOfOfficeSecretary', 'Deputy Team Leader'),
                    ('AssistantOfOfficeManagement', 'Group Executive Vice President'),
                    ('DirectorOfDirector', 'Vice President of Agency Administration Department'),
                    ('DirectorOfOffice', 'President/CEO'), 
                    ('DirectorOfOfficeSecretary', 'Senior Team Leader'),
                    ('project_head_preliminary_supervisor', 'Project head/Preliminary Supervisor'),
                    ('related_department', 'Related Group'),
                    ('deputy_director', 'Deputy Director'),
                    ('director', 'Director')]

STATE_APPROVE = [('pending', 'Pending'),
                 ('approve', 'Approve'),
                 ('reject', 'Reject')]

FIN_TYPE = [('eroe', 'Expense request of express'),
                   ('erob', 'Expense request of budget'),
                   ('proo', 'Purchase reguest of objective')]


class fw_pfb_FS100(models.Model):
    _name = 'fw_pfb_fin_system_100_history'
    _order = 'priority ASC, fin_date DESC, fin_no DESC'

    name = fields.Char(string='History No.' )
    fin100_origin = fields.Many2one('fw_pfb_fin_system_100',
                                 string='Origin FIN100')

    priority = fields.Selection(PRIORITY, string='Priority')
                                 
    fiscal_year = fields.Many2one('budget_system.fiscal_year')
    budget_system = fields.Many2one('budget_system.budget_system')
    budget_code = fields.Many2one('budget_system.budget_system_line')
    projects_and_plan = fields.Many2one('budget_system.projects_and_plan')
    budget_source = fields.Many2one('budget_system.budget_source')
    budget_department = fields.Many2one('hr.department')
    budget_request = fields.Float()

    # Fin system

    target_approver = fields.Char(string='Target Approver' )

    flow_template = fields.Many2one('fw_pfb_flow_template',  string='Flow Template')
                                 
    fin_objective = fields.Many2one('fw_pfb_objective',
                                 string='Objective')
    fin_type = fields.Selection(FIN_TYPE, string='FIN Type')

    participantas_quantity = fields.Char(string='Participantas Quantity', default="0")
    
    other = fields.Text(string='Other')
    estimate_output = fields.Text(string='Estimate')
    please_consider = fields.Selection(FIN_TYPE, string='Please Consider')


    fin_no = fields.Char(string='fin NO.',
                         readonly=True, )
    fin_date = fields.Date(string='fin Date',
                           default=lambda self: datetime.now(),
                           readonly=True)
    requester = fields.Many2one('hr.employee',
                                string='Requester')
    is_requester = fields.Boolean(string='Is requester')
    is_director = fields.Boolean(string="Is director")
    department = fields.Many2one('hr.department',
                                 string='Department',
                                 related='requester.department_id')
    state = fields.Selection(STATE_SELECTION,
                             default='draft',
                             required=True)
    subject = fields.Char(string='Subject')
    subject_to = fields.Char(string='Subject To.')
    objective = fields.Text(string='Objective Extra')
    participants = fields.Many2many('hr.employee')
    template_id = fields.Char(string='Template')
    fin_lines = fields.One2many('fw_pfb_fin_system_100_line_history',
                                'fin_id',
                                copy=True, )
    is_fin_lock = fields.Boolean(string="Lock")
    fin_ref = fields.Char(string='Reference')
    fin_remark = fields.Text(string='Remark')
    price_total = fields.Float(string='Request Amount')
    approver = fields.One2many('fw_pfb_fin_system_100_approver_history',
                               'fin_id',
                               copy=True,)
    approver_rights = fields.Char(string='Approver Rights')
    can_cancel = fields.Boolean(string='Can cancel')
    show_fin = fields.Boolean(string='Show FIN', )
    check_reject = fields.Boolean(string='Check Reject')
    fin_projects = fields.One2many('fw_pfb_fin_system_100_projects_history',
                                   'fin_id',
                                   copy=True,
                                   readonly=True)
    pr_ids = fields.Many2many("fw_ksp_pr",
                              string='Purchase Request',
                              readonly=True,
                              copy=False)
    pr_count = fields.Integer(string='PR Count')
    is_pr_created = fields.Boolean(string='Is PR Create?')

    can_set_complete = fields.Boolean(string='Can set to complete')



class fw_pfb_FS100Lines(models.Model):
    _name = 'fw_pfb_fin_system_100_line_history'

    fin_id = fields.Many2one('fw_pfb_fin_system_100_history',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)
    product_id = fields.Many2one('product.product',
                                 domain=[('fin_ok', '=', True)],
                                 required=True)
    is_pr_ok = fields.Boolean(related='product_id.pr_ok')
    description = fields.Char(string='description', )
    product_uom_qty = fields.Float(string='Quantity',
                                   # digits=dp.get_precision('Product Unit of Measure'),
                                   required=True,
                                   default=1.0)
    product_uom = fields.Many2one('product.uom',
                                  string='Unit of Measure',
                                  store=True,
                                  # related='product_id.product_tmpl_id.uom_id',
                                  required=True)
    price_unit = fields.Float('Unit Price',
                              required=True,
                              # digits=dp.get_precision('Product Price'),
                              store=True,
                              # default=_default_price,
                              # default='product_id.lst_price',
                              )
    price_subtotal = fields.Float(string='Subtotal',
                                  readonly=True,
                                  store=True, )
    projects_and_plan = fields.Many2one('budget_system.projects_and_plan',
                                        domain=[('type', '=', 'normal')])



class fw_pfb_FS100Approver(models.Model):
    _name = 'fw_pfb_fin_system_100_approver_history' 
    _order = 'position_index asc'     

    approve_active = fields.Boolean(string='Active')
    position_index = fields.Selection(POSITION_INDEX, string='Approve Position')

    fin_id = fields.Many2one('fw_pfb_fin_system_100_history',
                             required=True,
                             ondelete='cascade',
                             index=True)
    employee_id = fields.Many2one('hr.employee',
                                  required=True,
                                  domain=[('user_id', '!=', None),
                                          ('fin_can_approve', '=', True)])
    fin_position = fields.Selection(FIN_SELECTION, string='FIN Position')
    approve_position = fields.Selection(APPROVE_POSITION, string='Approve Position', required=True)
    employee_user_id = fields.Many2one('res.users',
                                       related='employee_id.user_id',
                                       readonly=True, )
    action_date = fields.Datetime(string='Action Date')
    state = fields.Selection(STATE_APPROVE,
                             string='State approve',
                             default='pending')
    memo = fields.Text(string='Memo')
    show_fin = fields.Boolean(string='Show FIN')
    is_related_department = fields.Boolean(string='Show FIN')
    is_not_related_department = fields.Boolean(string='Show FIN')

    employee_line = fields.One2many('fw_pfb_approve_employee_list_history', 'release_id', string='Please select employee')

    need_to_change_employee = fields.Boolean(string='Need to change employee', default=False)


class fw_pfb_FS100Budget(models.Model):
    _name = 'fw_pfb_fin_system_100_projects_history'

    fin_id = fields.Many2one('fw_pfb_fin_system_100_history',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)

    projects_and_plan = fields.Many2one('budget_system.projects_and_plan',
                                        readonly=True,)
    projects_residual = fields.Float(string='Residual',
                                     related='projects_and_plan.historical_amount',
                                     readonly=True)
    projects_reserve = fields.Float(string='Reserve',
                                    readonly=True)
    projects_residual_amount = fields.Float(string='Residual amount',
                                            readonly=True)

class fw_pfb_fin_system_100_approver_history(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_100_approver_history'

    memo = fields.Text('Memo', required=True)


class fw_pfb_approve_employee_list_history(models.TransientModel):
    _name = 'fw_pfb_approve_employee_list_history'

    release_id = fields.Many2one('fw_pfb_fin_system_100_approver')

    data_activate = fields.Boolean(string='Active')
    name = fields.Many2one('hr.employee', string='Employee Name')