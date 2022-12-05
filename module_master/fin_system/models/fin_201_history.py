# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from lxml import etree
import logging
from odoo.osv import orm
_logger = logging.getLogger(__name__)

POSITION_INDEX = [
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
    (6, 6), (7, 7), (8, 8), (9, 9), (10, 10),
    (11, 11), (12, 12), (13, 13), (14, 14), (15, 15),
    (16, 16), (17, 17), (18, 18), (19, 19), (20, 20)
]

PRIORITY = [
    ('1_normal', 'Normal'),
    ('0_urgent', 'Urgent')
]

FIN_TYPE = [
    ('parr', 'Payment and refund request')
]

FIN_TYPE_ON_FIN100 = [
    ('eroe', 'Expense request of express'),
    ('erob', 'Expense request of budget'),
    ('proo', 'Purchase reguest of objective'),
    ('parr', 'Payment and refund request')
]

POSITION_CLASS = {
    "DirectorOfDepartment": "fw_pfb_related_director_of_department",
    "DirectorOfEEC": "fw_pfb_related_directorofeec",
    "DirectorOfStrategy": "fw_pfb_related_directorofstrategy",
    "BudgetOwner": "fw_pfb_related_budgetowner",
    "DirectorOfFinance": "fw_pfb_related_directoroffinance",
    "ManagerOfStock": "fw_pfb_related_managerofstock",
    "AssistantOfOffice": "fw_pfb_related_assistantofoffice",
    "AssistantOfOfficeSecretary": "fw_pfb_related_assistantofoffice",
    "DeputyOfOffice": "fw_pfb_related_deputyofoffice",
    "DeputyOfOfficeSecretary": "fw_pfb_related_deputyofoffice",
    "AssistantOfOfficeManagement": "fw_pfb_related_assistantofofficemanagement",
    "DirectorOfDirector": "fw_pfb_related_directorofdirector",
    "DirectorOfOfficeSecretary": "fw_pfb_related_directorofoffice_secretary",
}

STATE_SELECTION = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('DirectorOfDepartment', 'Vice President/Director'),
    ('RelatedGroup', 'Related Group'),
    ('AssistantOfOffice', 'Executive Vice President'),
    ('DeputyOfOffice', 'Senior Executive Vice President'),
    ('SmallNote', 'Small Note'),
    ('DirectorOfOffice', 'Director'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('reject', 'Reject')
]

FIN_SELECTION = [
    ('DirectorOfDepartment', 'Vice President Director'),
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
    ('DirectorOfOfficeSecretary', 'Senior Team Leader')
]

APPROVE_POSITION = [
    ('DirectorOfDepartment', 'Vice President/Director'),
    ('RelatedGroup', 'Related Group'),
    ('DirectorOfFinance', 'Division Manager of Finance, Accounting and Control Division'),
    ('ManagerOfStock', 'Division Manager of General Affairs and Facilities Division'),
    ('AssistantOfOffice', 'Executive Vice President'),
    ('DeputyOfOffice', 'Senior Executive Vice President'),
    ('SmallNote', 'Small Note'),
    ('DirectorOfOffice', 'President/CEO')
]

STATE_APPROVE = [
    ('pending', 'Pending'),
    ('approve', 'Approve'),
    ('reject', 'Reject')
]

STATE_RESIDUAL = [
    ('no_residual', 'No Residual'), ('residual', 'Residual')
]

# SUBSIDIZED_CHOICES = [
#     ('depa_digital_startup_fund', 'DEPA Digital Startup Fund'),
#     ('depa_digital_transformation_fund', 'DEPA Digital Transformation Fund'),
#     ('depa_digital_research_development_and_innovation_fund', 'DEPA Digital Research Development and Innovation Fund'),
#     ('depa_digital_event_and_marketing_fund', 'DEPA Digital Event And Marketing Fund'),
#     ('depa_digital_infrastructure_fund_for_government_and_public_investment', 'DEPA Digital Infrastructure Fund for Government & Public Investment'),
#     ('depa_digital_infrastructure_fund_for_private_investment', 'DEPA Digital Infrastructure Fund for Private Investment'),
#     ('depa_digital_manpower_fund', 'DEPA Digital Manpower Fund'),
#     ('depa_scholarship', 'DEPA Scholarship'),
#     ('depa_digital_transformation_fund_for_commmunity', 'DEPA Digital Transformation Fund for Community'),
#     ('other', 'Other'),
# ]


class fw_pfb_FS201(models.Model):
    _name = 'fw_pfb_fin_system_201_history'
    _order = 'priority ASC, fin_date DESC, fin_no DESC'

    name = fields.Char(
        string='History No.'
    )
    fin201_origin = fields.Many2one(
        'fw_pfb_fin_system_201',
        string='Origin FIN201'
    )
    # Fin system

    priority = fields.Selection(PRIORITY, string='Priority', required=True)
    
    target_approver = fields.Char(string='Target Approver' )

    flow_template = fields.Many2one('fw_pfb_flow_template',
                                domain=[('type', '=', 'parr'),('data_activate', '=', True)],
                                string='Flow Template')

    fin_objective = fields.Many2one('fw_pfb_objective',
                                 string='Objective')
    fin_type = fields.Selection(FIN_TYPE, string='FIN Type', default="parr")

    participantas_quantity = fields.Char(string='Participantas Quantity', default="0")
    place = fields.Many2many("ir.attachment",
                                  "attachment_fin201_place_rel",
                                  "attachment_fin201_place_id",
                                  "attachment_id",
                                  string="Place")
    operation_date = fields.Many2many("ir.attachment",
                                  "attachment_fin201_operation_date_rel",
                                  "attachment_fin201_operation_date_id",
                                  "attachment_id",
                                  string="Operation Date")
    seminar_partcipants = fields.Many2many("ir.attachment",
                                  "attachment_fin201_seminar_rel",
                                  "attachment_fin201_seminar_id",
                                  "attachment_id",
                                  string="Seminar Partcipants")
    other = fields.Text(string='Other')
    estimate_output = fields.Text(string='Estimate')
    please_consider = fields.Selection(FIN_TYPE, string='Please Consider', default="parr")

    canedit_financial = fields.Boolean(
        string='Can Edit Financial Staff Verification',
        # compute='_is_canedit_financial',
        # default=_is_canedit_financial_default
    )

    fin_no = fields.Char(string='fin NO.',
                         readonly=True, )

    reference = fields.Char(
        string=_("Reference")
        )

    fin_date = fields.Date(
        string='fin Date',
        default=lambda self: date.today(),
        readonly=True
    )
    approved_amount = fields.Float(string='Approved amount')
    requester = fields.Many2one(
        'hr.employee',
        string='Requester',
        # default=_default_employee_get
    )
    is_requester = fields.Boolean(string='Is requester',
                                  # compute='_check_is_requester'
                                  )
    is_director = fields.Boolean(
        string="Is director",
        # compute='_get_approver_rights'
    )
    department = fields.Many2one(
        'hr.department',
        string='Department',
        related='requester.department_id',
    )
    actual_department_name = fields.Char(
        string='Department',
        # compute='_set_actual_department_name',
    )
    position = fields.Many2one('hr.job',
                               string='Position',
                               related='requester.job_id',
                               readonly=True)
    # emp_code = fields.Char(string='Employee code',
    #                        related='requester.es_employee_code',
    #                        readonly=True)
    state = fields.Selection(STATE_SELECTION,
                             default='draft',
                             required=True)
    subject = fields.Char(string='Subject')
    subject_to = fields.Char(string='Subject To.') 
    objective = fields.Text(string='Objective')
    objective_changed = fields.Text(string='Objective changed')
    participants = fields.Many2many('hr.employee')
    template_id = fields.Many2many('sale.order.template',
                                   'so_template_fin_rel',
                                   'so_id',
                                   'fin_id',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   domain=[('fin_ok', '=', True)])
    fin_lines = fields.One2many('fw_pfb_fin_system_201_line_history',
                                'fin_id',
                                copy=True, )
    is_fin_lock = fields.Boolean(string="Lock")
    fin_remark = fields.Text(string='Remark')

    request_amount_total = fields.Float(string='Request amount total', default=0)

    load_amount_total = fields.Float(string='Loan amount total', default=0)

    price_total = fields.Float(string='Total',
                               # compute='_compute_total'
                               )

    spent_amount_total  = fields.Float(string='Spent amount total', default=0)

    remaining_total  = fields.Float(string='Remaining amount paid / withdrawn', default=0)

    approver = fields.One2many('fw_pfb_fin_system_201_approver_history',
                               'fin_id',
                               copy=True,)
    approver_rights = fields.Char(
        string='Approver Rights',
        # compute="_get_approver_rights"
    )
    can_cancel = fields.Boolean(
        string='Can cancel',
        # compute='_check_can_cancel'
    )
    show_fin = fields.Boolean(string='Show FIN', )
    check_reject = fields.Boolean(string='Check Reject')
    attachment = fields.Many2many("ir.attachment",
                                  "attachment_fin201_rel",
                                  "attachment_fin201_id",
                                  "attachment_id",
                                  string="Attachment")
    account_memo = fields.Text(string="Accounting Memo.")

    # Flag for check request_to_cancel was checked
    is_request_to_cancel = fields.Boolean(
        string='Is request to cancel?',
        default=False,
    )

    allowed_to_cancel = fields.Boolean(
        string='Allowed to cancel',
        default=False,
    )

    can_approve_to_cancel = fields.Boolean(
        string='Can approve to cancel',
        default=False,
        # compute='_can_approve_to_cancel',
    )

    director_reject = fields.Boolean(
        default=False,
    )
    # To filter approver list
    approver_name_list = fields.Text(
        string='Approver Name',
        # compute='_compute_approver_list',
        store=True
    )
    # To filter filter in approver list
    action_date_list = fields.Text(
        string='Action Date Approved',
        # compute='_compute_approver_list',
        store=True,
    )
    subsidized_measurement = fields.Many2many(
        'subsidized.measurement',
        'subsidized_measurement_fin_rel',
        'fin_201_id',
        'subsidized_measure_id',
        string='Subsidized Measurement',
    )
    subsidized_measurement_other = fields.Char(
        string='Subsidized Measurement Other',
    )
    other_subsidized_flag = fields.Boolean(
        string='Other Subsidized Flag',
    )


class fw_pfb_FS201Lines(models.Model):
    _name = 'fw_pfb_fin_system_201_line_history'

    fin_type = fields.Selection(FIN_TYPE_ON_FIN100, string='FIN Type')
    fin_id = fields.Many2one('fw_pfb_fin_system_201_history',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)
    objective = fields.Text(string='Objective')
    fin100_number = fields.Many2one('fw_pfb_fin_system_100',string=_("FIN100 number"))
    fin_line_id = fields.Char(string='Fin line id' )
    product_id = fields.Many2one('product.template',
                                 domain=[('fin_ok', '=', True)],
                                 required=True)
    description = fields.Char(string='description', )
    product_uom_qty = fields.Float(string='Quantity',
                                   # digits=dp.get_precision('Product Unit of Measure'),
                                   required=True,
                                   default=1.0)
    product_uom = fields.Many2one('uom.uom',
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
    price_subtotal = fields.Float(
        # compute='_compute_subtotal',
        string='Subtotal',
        readonly=True,
        store=True,
    )
    projects_and_plan = fields.Many2one('account.analytic.account')

    loan_amount = fields.Float(string='Loan amount')
    payment_amount = fields.Float(string='Payment amount', default = 0)

    price_all_fin401 = fields.Float(
        'Price All Fin401',
        # compute="_compute_price_all_fin401"
    )
    pay_amount =  fields.Float('Pay', default = 0)


class fw_pfb_FS201Approver(models.Model):
    _name = 'fw_pfb_fin_system_201_approver_history'
    _order = 'position_index asc'

    approve_active = fields.Boolean(string='Active')
    position_index = fields.Selection(POSITION_INDEX, string='Approve Position')
    approve_position = fields.Selection(APPROVE_POSITION, string='Approve Position', required=True)
    employee_line = fields.One2many('fw_pfb_approve_employee_list201_history', 'release_id', string='Please select employee')
    need_to_change_employee = fields.Boolean(string='Need to change employee', default=False)

    fin_id = fields.Many2one('fw_pfb_fin_system_201_history',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)
    employee_id = fields.Many2one('hr.employee',
                                  required=True,
                                  domain=[('user_id', '!=', None),
                                          ('fin_can_approve', '=', True)])
    fin_position = fields.Selection(FIN_SELECTION, string='FIN Position')
    employee_user_id = fields.Many2one('res.users',
                                       related='employee_id.user_id',
                                       readonly=True, )
    action_date = fields.Datetime(string='Action Date', copy=False)
    state = fields.Selection(STATE_APPROVE,
                             string='State approve',
                             default='pending')
    memo = fields.Text(string='Memo', copy=False)
    show_fin = fields.Boolean(
        string='Show FIN',
        # compute=_show_fin
    )


class fw_pfb_FS201ApproveWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_201_approver_history'

    memo = fields.Text('Memo', required=True)

    
class fw_pfb_approve_employee_list(models.TransientModel):
    _name = 'fw_pfb_approve_employee_list201_history'

    release_id = fields.Many2one('fw_pfb_fin_system_201_approver_history')

    data_activate = fields.Boolean(string='Active')
    name = fields.Many2one('hr.employee', string='Employee Name')
