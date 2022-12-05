# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import logging
import base64
from odoo.osv import orm
_logger = logging.getLogger(__name__)
import pytz
from . import fin_middleware

DUMMY_EMPLOYEE = 4596
DEV_DUMMY_EMPLOYEE = 4595

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
                    ('DirectorOfOfficeSecretary', 'Senior Team Leader')]

STATE_APPROVE = [('pending', 'Pending'),
                 ('approve', 'Approve'),
                 ('reject', 'Reject')]

FIN_TYPE = [('eroe', 'Expense request of express'),
                   ('erob', 'Expense request of budget'),
                   ('proo', 'Purchase reguest of objective')]


class fw_pfb_FS100(models.Model):
    _name = 'fw_pfb_fin_system_100'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority ASC, fin_date DESC, fin_no DESC'

    # def _set_is_new_to_false(self):
    #     fin100 = self.env['fw_pfb_fin_system_100'].search([])
    #     for fin in fin100:
    #         fin.is_new = False

    @api.returns('self')
    def _default_employee_get(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.depends('approver')
    def _get_approver_rights(self):
        rights = ''
        approver_list = []
        for list in self.approver:
            approver_list.append(list.employee_user_id.id)
        if self._uid in approver_list:
            approver = self.env['fw_pfb_fin_system_100_approver'].search(
                [('fin_id', '=', self.id), ('employee_user_id.id', '=', self._uid)])
            if len(approver) > 1:
                for ap in approver:
                    rights += ap.fin_position + ' , '
            else:
                rights = approver.fin_position

        else:
            rights = 'fin_user'
        self.approver_rights = rights

    @api.depends('approver')
    def _get_is_director(self):
        rights = ''
        approver_list = []
        for list in self.approver:
            approver_list.append(list.employee_user_id.id)
        if self._uid in approver_list:
            approver = self.env['fw_pfb_fin_system_100_approver'].search(
                [('fin_id', '=', self.id), ('employee_user_id.id', '=', self._uid)])
            if len(approver) > 1:
                for ap in approver:
                    rights += ap.fin_position + ' , '
            else:
                rights = approver.fin_position

        else:
            rights = 'fin_user'
        if rights == 'director':
            self.is_director = True

    @api.depends('requester')
    def _check_is_requester(self):
        for rec in self:
            if rec._uid == rec.requester.user_id.id:
                rec.is_requester = True
            else:
                rec.is_requester = False

    @api.depends('can_set_complete')
    def _is_can_set_complete(self):
        self.can_set_complete = False
        usrid = self._uid
        active_model = self._name
        group_id = self.env['res.groups'].search([('name', 'like', 'Can change fin100 to complete')], limit=1)
        if group_id :
            if group_id.users :
                for i in group_id.users :
                    if i.id == usrid and active_model == 'fw_pfb_fin_system_100':
                        self.can_set_complete = True

    @api.multi
    def _check_can_cancel(self):
        fin_user = []
        for approver in self.approver:
            fin_user.append(approver.employee_user_id.id)
        fin_user.append(self.requester.user_id.id)
        if self._uid in fin_user:
            self.can_cancel = True
        else:
            self.can_cancel = False

    @api.depends('is_pr_created')
    def _get_pr(self):
        if self.is_pr_created:
            pr_list = []
            pr_obj = self.env['purchase.request'].search([('fin_id', '=', self.id)])
            for pr in pr_obj:
                pr_list.append(pr.id)
            self.pr_ids = pr_list
            self.pr_count = len(pr_obj)

    @api.onchange('fin_type')
    def _onchange_fin_type(self):
        self.approver = False
        self.flow_template_eroe = False
        self.flow_template_erob = False
        self.flow_template_proo = False
        self.please_consider = self.fin_type

    @api.onchange('flow_template_eroe', 'flow_template_erob', 'flow_template_proo')
    def _onchange_flow_template(self):
        self.approver = False
        id = False
        if self.flow_template_eroe :
            id = self.flow_template_eroe.id
        if self.flow_template_erob :
            id = self.flow_template_erob.id
        if self.flow_template_proo :
            id = self.flow_template_proo.id


        flow = self.env['fw_pfb_flow_template'].browse( id )
        # approver_line = []
        if flow :
            if flow.approve_line :
                for line in flow.approve_line :
                    data = {
                            "employee_id": line.emp_name.id,
                            "fin_position": line.position,
                            "approve_active": line.data_activate,
                            "approve_position": line.approve_position,
                            "position_index": line.position_index
                        }
                    if line.data_activate :
                        data["state"] = "pending"
                    # approver_line.append(data)
                    self.approver += self.approver.new( data )
                # self.approver = approver_line

    @api.one
    def _get_please_consider(self):
        self.please_consider = self.fin_type

    # Budget system

    projects_and_plan = fields.Many2one('account.analytic.account')

    budget_department = fields.Many2one('hr.department')
    budget_request = fields.Float()
    has_history = fields.Boolean(string="Has History", default = False)

    # Fin system

    priority = fields.Selection(PRIORITY, string='Priority', required=True)

    target_approver = fields.Char(string='Target Approver' )

    flow_template_eroe = fields.Many2one('fw_pfb_flow_template',
                                domain=[('type', '=', 'eroe'),('data_activate', '=', True)],
                                string='Flow Template')
    flow_template_erob = fields.Many2one('fw_pfb_flow_template',
                                DOMAIN=[('type', '=', 'erob'),('data_activate', '=', True)],
                                string='Flow Template')
    flow_template_proo = fields.Many2one('fw_pfb_flow_template',
                                domain=[('type', '=', 'proo'),('data_activate', '=', True)],
                                string='Flow Template')

    fin_objective = fields.Many2one(
        'fw_pfb_objective',
        string='Objective',
    )
    fin_type = fields.Selection(
        FIN_TYPE,
        string='FIN Type',
        required=True
    )

    participantas_quantity = fields.Char(string='Participantas Quantity', default="0")
    place = fields.Many2many("ir.attachment",
                                  "attachment_fin_place_rel",
                                  "attachment_fin_place_id",
                                  "attachment_id",
                                  string="Place")
    operation_date = fields.Many2many("ir.attachment",
                                  "attachment_fin_operation_date_rel",
                                  "attachment_fin_operation_date_id",
                                  "attachment_id",
                                  string="Operation Date")
    seminar_partcipants = fields.Many2many("ir.attachment",
                                  "attachment_fin_seminar_rel",
                                  "attachment_fin_seminar_id",
                                  "attachment_id",
                                  string="Seminar Partcipants")
    other = fields.Text(string='Other')
    estimate_output = fields.Text(string='Estimate')
    please_consider = fields.Selection(FIN_TYPE, string='Please Consider', compute="_get_please_consider")


    fin_no = fields.Char(string='fin NO.',
                         readonly=True, )
    fin_date = fields.Date(string='fin Date',
                           # default=lambda self: datetime.now(),
                           default=lambda self: date.today(),
                           readonly=True)
    requester = fields.Many2one('hr.employee',
                                string='Requester',
                                default=_default_employee_get)
    is_requester = fields.Boolean(string='Is requester',
                                  compute='_check_is_requester')
    is_director = fields.Boolean(string="Is director",
                                 compute='_get_is_director')
    department = fields.Many2one('hr.department',
                                 string='Department',
                                 related='requester.department_id')
    actual_department_name = fields.Char(string='Department',
                                         compute='_set_actual_department_name',)
    state = fields.Selection(STATE_SELECTION,
                             default='draft',
                             required=True)
    subject = fields.Char(string='Subject')
    subject_to = fields.Char(string='Subject To.')
    objective = fields.Text(
        string='Objective Extra',
    )
    participants = fields.Many2many('hr.employee')
    template_id = fields.Many2many('sale.order.template',
                                   'so_template_fin_rel',
                                   'so_id',
                                   'fin_id',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   domain=[('fin_ok', '=', True)])
    fin_lines = fields.One2many('fw_pfb_fin_system_100_line',
                                'fin_id',
                                copy=True, )
    is_fin_lock = fields.Boolean(string="Lock")
    fin_ref = fields.Char(string='Reference')
    fin_remark = fields.Text(string='Remark')
    price_total = fields.Float(string='Request Amount', compute='_compute_total')
    approver = fields.One2many('fw_pfb_fin_system_100_approver',
                               'fin_id',
                               copy=True,)
    approver_rights = fields.Char(string='Approver Rights',
                                  compute="_get_approver_rights")
    can_cancel = fields.Boolean(string='Can cancel',
                                compute='_check_can_cancel')
    show_fin = fields.Boolean(string='Show FIN', )
    check_reject = fields.Boolean(string='Check Reject')
    fin_projects = fields.One2many('fw_pfb_fin_system_100_projects',
                                   'fin_id',
                                   copy=True,
                                   readonly=True)
    attachment = fields.Many2many("ir.attachment",
                                  "attachment_fin_rel",
                                  "attachment_fin_id",
                                  "attachment_id",
                                  string="Attachment")
    can_create_pr = fields.Boolean(compute='_check_can_be_pr')
    is_fin_open = fields.Boolean()
    pr_ids = fields.Many2many("purchase.request",
                              string='Purchase Request',
                              compute="_get_pr",
                              readonly=True,
                              copy=False)
    pr_count = fields.Integer(string='PR Count',
                              compute='_get_pr')
    is_pr_created = fields.Boolean(string='Is PR Create?')

    can_set_complete = fields.Boolean(string='Can set to complete', compute="_is_can_set_complete")

    # This fields to use cross department means FIN100 usable in FIN201 and FIN401
    can_cross_department = fields.Boolean(
        string='Can Cross Department',
        default=False,
    )

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
        compute='_can_approve_to_cancel',
    )

    director_reject = fields.Boolean(
        default=False,
    )

    # Attachment Fields when fin_type = 'proo'
    attachment_base_price = fields.Many2many("ir.attachment",
                                  "attachment_base_price_fin_rel",
                                  "attachment_base_price_fin_id",
                                  "attachment_base_price_id",
                                  string="Attachment Base Price")
    attachment_work_scope = fields.Many2many("ir.attachment",
                                  "attachment_work_scope_fin_rel",
                                  "attachment_work_scope_fin_id",
                                  "attachment_work_scope_id",
                                  string="Attachment Work Scope")
    attachment_participants = fields.Many2many("ir.attachment",
                                             "attachment_participants_fin_rel",
                                             "attachment_participants_fin_id",
                                             "attachment_participants_id",
                                             string="Attachment Participants")
    attachment_memo = fields.Many2many("ir.attachment",
                                       "attachment_memo_fin_rel",
                                       "attachment_memo_fin_id",
                                       "attachment_memo_id",
                                       string="Attachment Memo")

    # To store Cancel reason (memo fields) from fw_pfb_fin_system_100_request_to_cancel_request
    cancel_reason = fields.Text()

    # To filter approver list
    approver_name_list = fields.Text(
        string='Approver Name',
        compute='_compute_approver_list',
        store=True
    )
    # To filter filter in approver list
    action_date_list = fields.Text(
        string='Action Date Approved',
        compute='_compute_approver_list',
        store=True,
    )

    @api.multi
    @api.depends('approver')
    def _compute_approver_list(self):
        for rec in self:
            approver_list = ''
            action_list = ''
            if rec.approver:
                for ap in rec.approver:
                    if ap.employee_id.name:
                        approver_list += ap.employee_id.name + ' '
                    if ap.action_date:
                        action_list += str(ap.action_date)
                rec.approver_name_list = approver_list
                rec.action_date_list = action_list


    @api.onchange('fin_objective')
    @api.multi
    def _onchage_fin_objective(self):
        print("FIN_100.onchange_fin_objective")
        for rec in self:
            if rec.fin_objective:
                rec.objective = rec.fin_objective.description

    @api.constrains(
        'attachment_base_price',
        'attachment_work_scope',
        'attachment_participants',
        'attachment_memo'
    )
    def _attachment_depends(self):
        if self.attachment_base_price is None:
            print('Test')

    # @api.onchange('fin_lines')
    # def _onchange_fin_lines(self):
    #     print('FIN _LINES ')

    @api.multi
    def _can_approve_to_cancel(self):
        director_id = []
        for obj in self:
            director = self.env['fw_pfb_fin_settings2'].sudo().search([])
            for directoroffice in director.directorOfOffice.user_id:
                director_id.append(directoroffice.id)
            if self._uid in director_id:
                obj.can_approve_to_cancel = True

    # @api.onchange('is_fin_open')
    # def _onchange_is_fin_open(self):
    #     print('IS FIN OPEN')
        # if self.is_fin_close:
        #     fin_return_balance = 0.0
        #     for fin_project in self.fin_projects:
        #         fin_line_obj = self.env['fw_pfb_fin_system_100_line'].search([
        #             ('fin_id', '=', self.id),
        #             ('projects_and_plan', '=', fin_project.projects_and_plan.id)
        #         ])
        #         for fin_line in fin_line_obj:
        #             fin_return_balance += fin_line.balance
        #         fin_project.projects_return = fin_return_balance

        # if not fin.is_fin_close:
        #     if fin.fin_projects:
        #         for project in fin.fin_projects:
        #             fin_return_balance = 0.0
        #             fin100_line_obj = self.env['fw_pfb_fin_system_100_line'].search([
        #                 ('fin_id', '=', fin.id),
        #                 ('projects_and_plan', '=', project.projects_and_plan.id),
        #             ])
        #             # Calculate project balance
        #             for flo in fin100_line_obj:
        #                 fin_return_balance += flo.balance
        #             project.projects_return = fin_return_balance

    @api.multi
    def action_fin_open(self):
        for fin in self:
            fin.is_fin_open = not fin.is_fin_open
        if not self.is_fin_open:
            fin_return_balance = 0.0
            for fin_project in self.fin_projects:
                fin_line_obj = self.env['fw_pfb_fin_system_100_line'].search([
                    ('fin_id', '=', self.id),
                    ('projects_and_plan', '=', fin_project.projects_and_plan.id)
                ])
                for fin_line in fin_line_obj:
                    fin_return_balance += fin_line.balance
                fin_project.write({
                    'projects_return': fin_return_balance
                })
                if fin_project.projects_and_plan:
                    # Recompute
                    fin_project.projects_and_plan.button_force_reset_fin100_lines()
                    fin_project.projects_and_plan.button_force_compute_fin100_lines()
            # Stamp Log
            # employee_obj = self.env['hr.employee'].search([
            #     ('user_id', '=', self._uid),
            # ])
            # if employee_obj:
            #     user_name = _("%s" % employee_obj.name)
            # else:
            #     user_obj = self.env['res.users'].search([
            #         ('id', '=', self._uid),
            #     ])
            #     user_name = _("%s" % user_obj.name)
            # self.message_post(
            #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
            #         "SYSTEM LOG",
            #         "Employee" if employee_obj else "User",
            #         str(user_name),
            #         "FIN100 Close",
            #         str(self.write_date),
            #     ))
            # )
            log_message = fin_middleware.message_log_stamp(self, "FIN100 Close", self.write_date)
            self.message_post(body=_(log_message))
        else:
            for fin_project in self.fin_projects:
                fin_project.write({
                    'projects_return': 0.0
                })
                if fin_project.projects_and_plan:
                    # Recompute
                    fin_project.projects_and_plan.button_force_reset_fin100_lines()
                    fin_project.projects_and_plan.button_force_compute_fin100_lines()
            # Stamp Log
            # employee_obj = self.env['hr.employee'].search([
            #     ('user_id', '=', self._uid),
            # ])
            # if employee_obj:
            #     user_name = _("%s" % employee_obj.name)
            # else:
            #     user_obj = self.env['res.users'].search([
            #         ('id', '=', self._uid),
            #     ])
            #     user_name = _("%s" % user_obj.name)
            # self.message_post(
            #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
            #         "SYSTEM LOG",
            #         "Employee" if employee_obj else "User",
            #         str(user_name),
            #         "FIN100 Open",
            #         str(self.write_date),
            #     ))
            # )
            log_message = fin_middleware.message_log_stamp(self, "FIN100 Open", self.write_date)
            self.message_post(body=_(log_message))


    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, fin_date=date.today())
        return super(fw_pfb_FS100, self).copy(default)

    @api.multi
    def _set_actual_department_name(self):
        for record in self:
            record.actual_department_name = record.department.name


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_fin = self.env['fw_pfb_fin_system_100']
        env_fin_approver = self.env['fw_pfb_fin_system_100_approver']
        params = self._context.get('params')

        checkRule = False

        if params :
            if "action" in params :
               if params["action"] == 1111 :
                   checkRule = True

        res = super(fw_pfb_FS100, self).fields_view_get(
                view_id=view_id, view_type=view_type, toolbar=toolbar,
                submenu=submenu)

        if checkRule :
            fin_list = env_fin.search([])
            for fin in fin_list:
                fin_user = []
                fin_obj = env_fin.search([('id', '=', fin.id)])
                # fin_user.append(fin_obj.requester.user_id.id)
                if fin_obj.check_reject != True :
                    fin_obj_approve = env_fin_approver.search([
                        ('fin_id', '=', fin.id),
                        ('approve_active', '=', True)
                    ])

                    for approver in fin_obj_approve :
                        if fin_obj.target_approver == approver.approve_position :
                            if approver.employee_user_id :
                                if approver.state == "pending" or approver.state == False :
                                    fin_user.append( approver.employee_user_id.id )

                        if fin_obj.target_approver == "DirectorOfOffice" :
                            if approver.approve_position == "SmallNote" :
                                if approver.state == False or approver.state == "pending" :
                                    if approver.employee_user_id :
                                        fin_user.append( approver.employee_user_id.id )

                        if approver.approve_position == "DirectorOfOffice" :
                            directorCanSee = False
                            for checker in fin_obj_approve :
                                if checker.approve_active and checker.approve_position != "DirectorOfOffice" :
                                    if checker.approve_position == "DirectorOfFinance" or checker.approve_position == "ManagerOfStock" or checker.approve_position == "AssistantOfOffice" or checker.approve_position == "DeputyOfOffice" or checker.approve_position == "SmallNote" :
                                        if checker.state == "approve" :
                                            directorCanSee = True

                            if directorCanSee :
                                if approver.employee_user_id :
                                    fin_user.append( approver.employee_user_id.id )

                if self._uid in fin_user:
                    if not fin_obj.show_fin : # if show_fin is False
                        fin_obj.show_fin = True
                else:
                    if fin_obj.show_fin : # if show_fin is True
                        fin_obj.show_fin = False
        return res

    @api.multi
    def fin100_history(self):
        history_ids = self.env['fw_pfb_fin_system_100_history'].search([('fin100_origin','=',self.id)])

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('fin_system.fin_system_100_request_history_action')
        list_view_id = imd.xmlid_to_res_id('fin_system_100_request_history_tree_view')
        form_view_id = imd.xmlid_to_res_id('fin_system_100_request_history_form_view')

        newcontext = eval(action.context).copy()

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': '%s' % newcontext,
            'res_model': action.res_model,
        }

        if len(history_ids) >= 1:
            result['domain'] = "[('id','in',%s)]" % [x.id for x in history_ids]
        else:
            result['domain'] = "[('id','=',0)]"

        return result


    @api.multi
    def name_get(self):
        return [(cat.id, cat.fin_no) for cat in self]

    @api.model
    def create(self, vals):
        vals['fin_no'] = self.env['ir.sequence'].next_by_code('seq_fw_pfb_fin_100')
        if "approver" in vals :
            for ap in vals["approver"] :
                if len(ap) == 3 :
                    datas = ap[2]
                    if "approve_active" in datas :
                        if datas["approve_active"] == True :
                            if "employee_id" in datas :
                                # Change to DUMMY Flag
                                emp_obj = self.env['hr.employee'].search([
                                    ('id', '=', datas['employee_id']),
                                    ('is_dummy', '=', True),
                                ])
                                if emp_obj:
                                # if datas["employee_id"] == DUMMY_EMPLOYEE or datas["employee_id"] == DEV_DUMMY_EMPLOYEE :
                                    raise UserError(_("Don't use Dummy employee on approver."))

        #order = {key[0]: i for i, key in enumerate(FIN_SELECTION)}
        #sorted_approver = sorted(vals['approver'], key=lambda kv: order[kv[2]['fin_position']])
        #vals['approver'] = sorted_approver
        res = super(fw_pfb_FS100, self).create(vals)

        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        
        # localize_datetime = self.get_localize_time()
        # user = self.env['res.users'].browse(self._uid)
        # if user.tz:
        #     tz = pytz.timezone(user.tz) or pytz.utc
        #     localize_datetime = pytz.utc.localize(res.create_date).astimezone(tz)
        # else:
        #     localize_datetime = res.create_date
        # localize_datetime = localize_datetime.strftime("%d/%m/%Y, %H:%M:%S")
        # localize_datetime = fin_middleware.localized_datetime(self, res.create_date)
        log_message = fin_middleware.message_log_stamp(self, "Create FIN100", res.create_date)
        res.message_post(body=_(log_message))
        # res.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Create FIN100",
        #         str(localize_datetime),
        #     ))
        # )

        return res

    @api.multi
    def fin_sent_to_supervisor(self):
        targetApprover = 'DirectorOfDepartment'

        list = []

        if self.approver :
            for appr in self.approver :
                if appr.approve_active :
                    if appr.approve_position :
                        astate = appr.approve_position
                        if astate not in list :
                            list.append( astate )

            if "DirectorOfDepartment" in list :
                targetApprover = 'DirectorOfDepartment'
            elif "RelatedGroup" in list :
                targetApprover = 'RelatedGroup'
            elif "DirectorOfFinance" in list :
                targetApprover = 'DirectorOfFinance'
            elif "AssistantOfOffice" in list :
                targetApprover = 'AssistantOfOffice'
            elif "DeputyOfOffice" in list :
                targetApprover = 'DeputyOfOffice'
            elif "SmallNote" in list :
                targetApprover = 'SmallNote'
            elif "DirectorOfOffice" in list :
                targetApprover = 'DirectorOfOffice'

        self.write({
            'state': 'sent',
            'target_approver' : targetApprover
        })

        if self.fin_lines :
            for fl in self.fin_lines :
                fl.write({
                    'fin100_state': 'sent'
                })

        return True

    @api.multi
    def fin_create_pr(self):
        return {
                'name': "Purchase Request",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.fin.system.100.create.pr',
                'target': 'new',
                'context': {
                    'fin_100_id': self.id,
                    'default_pr_name': 'test'
                },
        }
    # @api.multi
    # def fin_create_pr(self):
    #     if self.state == 'completed':
    #         vals = {}
    #         proj_n_plan = None
    #         request_lines = {}
    #         i = 0
    #         for line in self.fin_lines:
    #             if line:
    #                 i += 1
    #                 if line.projects_and_plan:
    #                     proj_n_plan = line.projects_and_plan.id
    #
    #                 request_lines[i] = {
    #                     'product_id': line.product_id.id,
    #                     'name': line.description,
    #                     'product_qty': line.product_uom_qty,
    #                     'product_uom_id': line.product_uom.id,
    #                     'analytic_account_id': proj_n_plan,
    #                     'estimated_cost': line.price_unit,
    #                 }
    #
    #                 vals = {
    #                     'fin_id': self.id,
    #                     'origin': self.fin_no,
    #                     'requested_by': self.requester.user_id.id,
    #                     'department_id': self.department.id,
    #                     'description': self.objective,
    #                 }
    #
    #                 res = self.env['purchase.request'].create(vals)
    #                 for line in request_lines:
    #                     request_lines[line]['request_id'] = res.id
    #                     res.line_ids.create(request_lines[line])
    #                    

                    # # Declare res_model use for attachment stamp
                    # attachment_res_model = 'purchase.request'
                    #    
                    # # Prepare attachment data
                    # if self.attachment_base_price:
                    #     vals['pr_ck'] = True
                    #     attribute_pr_id = {}
                    #     for key, attachment in enumerate(self.attachment_base_price):
                    #         attribute_pr_id[key] = self.env['ir.attachment'].create({
                    #             'name': attachment.name,
                    #             'datas': attachment.datas,
                    #             'datas_fname': attachment.datas_fname,
                    #             'res_model': attachment_res_model,
                    #             'res_id': 0,
                    #         }).id
                    # if self.attachment_work_scope:
                    #     vals['pr2_ck'] = True
                    #     middle_price_id = {}
                    #     for key, attachment in enumerate(self.attachment_work_scope):
                    #         middle_price_id[key] = self.env['ir.attachment'].create({
                    #             'name': attachment.name,
                    #             'datas': attachment.datas,
                    #             'datas_fname': attachment.datas_fname,
                    #             'res_model': attachment_res_model,
                    #             'res_id': 0,
                    #         }).id
                    # if self.attachment_participants:
                    #     vals['pr3_ck'] = True
                    #     attachment_participants_id = {}
                    #     for key, attachment in enumerate(self.attachment_participants):
                    #         attachment_participants_id[key] = self.env['ir.attachment'].create({
                    #             'name': attachment.name,
                    #             'datas': attachment.datas,
                    #             'datas_fname': attachment.datas_fname,
                    #             'res_model': attachment_res_model,
                    #             'res_id': 0,
                    #         }).id
                    # if self.attachment_memo:
                    #     vals['pr4_ck'] = True
                    #     attachment_memo_id = {}
                    #     for key, attachment in enumerate(self.attachment_memo):
                    #         attachment_memo_id[key] = self.env['ir.attachment'].create({
                    #             'name': attachment.name,
                    #             'datas': attachment.datas,
                    #             'datas_fname': attachment.datas_fname,
                    #             'res_model': attachment_res_model,
                    #             'res_id': 0,
                    #         }).id
                    # ###
                    #    
                    # pr_obj = self.env['purchase.request'].search([
                    #     ('fin_id', '=', self.id),
                    # ], limit=1)
                    # if pr_obj:
                    #     pr_obj.write(vals)
                    #     pr_obj.line_ids.unlink()
                    #     for line in request_lines:
                    #         request_lines[line]['request_id'] = pr_obj.id
                    #         pr_obj.line_ids.create(request_lines[line])
                    #     res = pr_obj
                    # else:
                    #     res = self.env['purchase.request'].create(vals)
                    #     # INSERT attachment to attribute_pr field
                    #     if vals['pr_ck']:
                    #         for api in attribute_pr_id:
                    #             self.env.cr.execute(
                    #                 """INSERT INTO attachment_attribute_pr_rel(attachment_attribute_pr_id, attachment_id)
                    #                 VALUES(%d, %d);""" %
                    #                 (res.id, attribute_pr_id[api])
                    #             )
                    #     # INSERT attachment to middle_price field
                    #     if vals['pr2_ck']:
                    #         for mpi in middle_price_id:
                    #             self.env.cr.execute(
                    #                 """INSERT INTO attachment_middle_price_rel(attachment_middle_price_id, attachment_id)
                    #                 VALUES(%d, %d);""" %
                    #                 (res.id, middle_price_id[mpi])
                    #             )
                    #     # INSERT attachment to attribute_pr2 field
                    #     if vals['pr3_ck']:
                    #         for api in attachment_participants_id:
                    #             self.env.cr.execute(
                    #                 """INSERT INTO attachment_attribute_pr2_rel(attachment_attribute_pr2_id, attachment_id)
                    #                 VALUES(%d, %d);""" %
                    #                 (res.id, attachment_participants_id[api])
                    #             )
                    #     # INSERT attachment to attribute_pr3 field
                    #     if vals['pr4_ck']:
                    #         for ami in attachment_memo_id:
                    #             self.env.cr.execute(
                    #                 """INSERT INTO attachment_attribute_pr3_rel(attachment_attribute_pr3_id, attachment_id)
                    #                 VALUES(%d, %d);""" %
                    #                 (res.id, attachment_memo_id[ami])
                    #             )
                    #    
                    #     self.is_pr_created = True
                    #     for line in request_lines:
                    #         request_lines[line]['request_id'] = res.id
                    #         self.env['purchase.request.line'].create(request_lines[line])
                    #    
                    # res.attribute_pr.write({
                    #     'res_model': 'purchase.request',
                    #     'res_id': res.id,
                    # })
    
            # return {
            #     'name': "Purchase Request",
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'purchase.request',
            #     'res_id': res.id,
            #     'type': 'ir.actions.act_window',
            # }


    # @api.multi
    # def fin_create_purchase_request(self):
        # vals = {}
        # proj_n_plan = None
        # request_lines = {}
        # i = 0
        # for line in self.fin_lines:
        #     if line.is_pr_ok:
        #         i += 1
        #         request_lines[i] = {
        #             'product_id': line.product_id.id,
        #             'name': line.description,
        #             'product_qty': line.product_uom_qty,
        #             'product_uom': line.product_uom.id,
        #             'price_unit': line.price_unit
        #         }
        #         if line.projects_and_plan:
        #             proj_n_plan = line.projects_and_plan.id
        #
        #         vals = {
        #             'fin_id': self.id,
        #             'projects_and_plan': proj_n_plan,
        #             'budget_request': self.price_total,
        #         }
        #         res = self.env['fw_ksp_pr'].create(vals)
        #         self.is_pr_created = True
        #         for line in request_lines:
        #             request_lines[line]['request_id'] = res.id
        #             self.env['fw_ksp_pr.line'].create(request_lines[line])
        # return res

    @api.multi
    def change_to_complete(self):
        self.write({
            'state': 'completed'
        })

        if self.fin_lines :
            for fl in self.fin_lines :
                fl.write({
                    'fin100_state': 'completed'
                })

        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Set to Complete",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "Set to Complete", self.write_date)
        self.message_post(body=_(log_message))

        return True

    @api.multi
    def fin_complete(self):
        self.write({
            'state': 'completed',
            'target_approver' : False
        })

        if self.fin_lines :
            for fl in self.fin_lines :
                fl.write({
                    'fin100_state': 'completed'
                })

        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br /> Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Complete FIN100",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "Complete FIN100", self.write_date)
        self.message_post(body=_(log_message))

        return True

    @api.multi
    def fin_request_to_cancel(self):
        self.write({
            'is_request_to_cancel': True,
        })
        # # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Request to Cancel",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "Request to Cancel", self.write_date)
        self.message_post(body=_(log_message))
        return True

    @api.multi
    def action_approve_to_cancel(self):
        self.write({
            'allowed_to_cancel': True,
        })
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Approve to Cancel",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "Approve to Cancel", self.write_date)
        self.message_post(body=_(log_message))

        return True

    @api.multi
    def fin_cancel(self):
        self.write({
            'state': 'cancelled',
            'allowed_to_cancel': False,
            'can_approve_to_cancel': False,
            'is_request_to_cancel': False
        })

        if self.fin_lines :
            for fl in self.fin_lines :
                fl.write({
                    'fin100_state': 'cancelled'
                })

        for fin_project in self.fin_projects:
            fin_project.projects_return = fin_project.projects_reserve

            if fin_project.projects_and_plan:
                # Recompute
                fin_project.projects_and_plan.button_force_reset_fin100_lines()
                fin_project.projects_and_plan.button_force_compute_fin100_lines()
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "FIN100 Cancel",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "FIN100 Cancel", self.write_date)
        self.message_post(body=_(log_message))
        return True

    @api.multi
    def fin_set_to_draft(self):

        f100h = self.env['fw_pfb_fin_system_100_history'].search([('fin100_origin', '=', self.id)])
        countHistory = 0

        self.fin_date = date.today()
        self.is_fin_open = True
        self.can_approve_to_cancel = False
        self.allowed_to_cancel = False
        self.is_request_to_cancel = False


        if f100h :
            countHistory = len( f100h )

        datas = {
            "name" : "Reject FIN100 No." + self.fin_no + " / " + str( countHistory + 1 ),
            "fin_no" : "Reject FIN100 No." + self.fin_no + " / " + str( countHistory + 1 ),
            "fin100_origin" : self.id,
            "fin_type" : self.fin_type,
            "fin_date" : self.fin_date,
            "subject" : self.subject,
            "subject_to" : self.subject_to,
            "fin_ref" : self.fin_ref,
            "objective" : self.objective,
            "participantas_quantity" : self.participantas_quantity,
            "other" : self.other,
            "estimate_output" : self.estimate_output,
            "please_consider" : self.please_consider,
            "fin_remark" : self.fin_remark,
            "is_fin_lock" : self.is_fin_lock,
            "state" : self.state,
            "price_total" : self.price_total
        }

        if self.requester :
            datas["requester"] = self.requester.id
        if self.department :
            datas["department"] = self.department.id
        if self.fin_objective :
            datas["fin_objective"] = self.fin_objective.id

        temp = ""
        if self.template_id :
            for i in self.template_id :
                if temp != "" :
                    temp += ", "
                temp += i.name

            datas["template_id"] = temp

        if self.flow_template_eroe :
            datas["flow_template"] = self.flow_template_eroe.id
        elif  self.flow_template_erob :
            datas["flow_template"] = self.flow_template_erob.id
        elif  self.flow_template_proo :
            datas["flow_template"] = self.flow_template_proo.id

        hid = self.env['fw_pfb_fin_system_100_history'].create( datas )

        for each in self.fin_lines :
            data = {
                    "fin_id" : hid.id,
                    "description" : each.description,
                    "product_uom" : each.product_uom.id,
                    "product_uom_qty" : each.product_uom_qty,
                    "price_unit" : each.price_unit,
                    "price_subtotal" : each.price_subtotal,
                    "product_id" : each.product_id.id,
                    "projects_and_plan" : each.projects_and_plan.id
                }
            self.env['fw_pfb_fin_system_100_line_history'].create( data )

        for each in self.fin_projects :
            data = {
                    "fin_id" : hid.id,
                    "projects_and_plan" : each.projects_and_plan.id,
                    "projects_residual" : each.projects_residual,
                    "projects_reserve" : each.projects_reserve,
                    "projects_residual_amount" : each.projects_residual_amount
                }
            self.env['fw_pfb_fin_system_100_projects_history'].create( data )

        for each in self.approver :
            data = {
                    "fin_id" : hid.id,
                    "position_index" : each.position_index,
                    "employee_id" : each.employee_id.id,
                    "fin_position" : each.fin_position,
                    "approve_position" : each.approve_position,
                    "action_date" : each.action_date,
                    "state" : each.state,
                    "memo" : each.memo,
                }
            self.env['fw_pfb_fin_system_100_approver_history'].create( data )

        for approver in self.approver:
            approver.write({
                'memo': '',
                'action_date': None,
                'state': 'pending',
            })


        if self.fin_lines :
            for fl in self.fin_lines :
                fl.write({
                    'fin100_state': 'draft'
                })

        self.write({
            'state': 'draft',
            'target_approver' : False,
            'check_reject': False,
        })

        if self.fin_projects:
            for fin_project in self.fin_projects:
                fin_project.projects_return = 0

                if fin_project.projects_and_plan:
                    # Recompute
                    fin_project.projects_and_plan.button_force_reset_fin100_lines()
                    fin_project.projects_and_plan.button_force_compute_fin100_lines()

        return True

    @api.multi
    def fin_lock(self):
        self.write({
            'is_fin_lock': True
        })
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "FIN100 Lock",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "FIN100 Lock", self.write_date)
        self.message_post(body=_(log_message))
        return True

    @api.multi
    def fin_unlock(self):
        self.write({
            'is_fin_lock': False
        })
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "FIN100 Unlock",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "FIN100 Unlock", self.write_date)
        self.message_post(body=_(log_message))
        return True

    @api.multi
    def action_view_fin(self):
        pr_ids = self.mapped('pr_ids')
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('purchase_request.purchase_request_form_action')
        list_view_id = imd.xmlid_to_res_id('purchase_request.view_purchase_request_tree')
        form_view_id = imd.xmlid_to_res_id('purchase_request.view_purchase_request_form')

        result = {
            'name': action.name,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(pr_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % pr_ids.ids
        elif len(pr_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = pr_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    # @api.multi
    # def fin_create_purchase_request(self):
    #     vals = {}
    #     proj_n_plan = None
    #     request_lines = {}
    #     i = 0
    #     for line in self.fin_lines:
    #         if line.is_pr_ok:
    #             i += 1
    #             request_lines[i] = {
    #                 'product_id': line.product_id.id,
    #                 'name': line.description,
    #                 'product_qty': line.product_uom_qty,
    #                 'product_uom': line.product_uom.id,
    #                 'price_unit': line.price_unit
    #             }
    #             if line.projects_and_plan:
    #                 proj_n_plan = line.projects_and_plan.id
    #
    #             vals = {
    #                 'fin_id': self.id,
    #                 'projects_and_plan': proj_n_plan,
    #                 'budget_request': self.price_total,
    #             }
    #             res = self.env['fw_ksp_pr'].create(vals)
    #             self.is_pr_created = True
    #             for line in request_lines:
    #                 request_lines[line]['request_id'] = res.id
    #                 self.env['fw_ksp_pr.line'].create(request_lines[line])
    #     return res

    @api.multi
    @api.depends('fin_lines.price_subtotal')
    def _compute_total(self):
        for fin in self:
            total = 0
            for line in fin.fin_lines:
                total += line.price_subtotal
            fin.price_total = total

    @api.multi
    @api.depends('fin_lines.is_pr_ok')
    def _check_can_be_pr(self):
        for fin in self.fin_lines:
            if fin.is_pr_ok:
                self.can_create_pr = True

    @api.onchange('template_id')
    def _onchange_template(self):
        new_lines = []
        for tp_id in self.template_id:
            quote_template = self.env['sale.order.template.line'].sudo().search([('sale_order_template_id', '=', tp_id.id)])
            for quote_line in quote_template:
                new_lines.append((0, 0, {
                    'product_id': quote_line.product_id.id,
                    'description': quote_line.name,
                    'standard_price': quote_line.price_unit,
                    'price_unit': quote_line.price_unit,
                    'product_uom_qty': quote_line.product_uom_qty,
                    'product_uom': quote_line.product_uom_id.id,
                    'fin100_state' : "draft"
                }))
        self.fin_lines = new_lines


class fw_pfb_FS100Lines(models.Model):
    _name = 'fw_pfb_fin_system_100_line'

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_subtotal(self):
        for line in self:
            line['price_subtotal'] = line.product_uom_qty * line.price_unit

    @api.one
    def _compute_price_all_fin201(self):
        for rec in self :
            total = 0
            lines = self.env["fw_pfb_fin_system_201_line"].search( [("fin_line_id", "=", str( rec.id ) )] )
            if lines :
                for line in lines :
                    total += line.payment_amount

                rec.price_all_fin201 = total

    @api.one
    def _compute_price_all_fin401(self):
        for rec in self :
            total = 0
            lines = self.env["fw_pfb_fin_system_401_line"].search( [("fin_line_id", "=", str( rec.id ) )] )
            if lines :
                for line in lines :
                    total += line.lend

                rec.price_all_fin401 = total


    @api.constrains('price_unit')
    def _validation_price_unit(self):
        for line in self:
            if line.price_unit < 0:
                raise ValidationError(_('Unit Price must greater than zero'))

    # @api.one
    # def _compute_projects_and_plan_year(self):
    #     for rec in self :
    #         if rec.projects_and_plan :
    #             if rec.projects_and_plan.fiscal_year :
    #                 rec.projects_and_plan_year = rec.projects_and_plan.fiscal_year.name

    # @api.onchange('projects_and_plan')
    # def _onchange_projects_and_plan_year(self):
    #     if self.projects_and_plan :
    #         if self.projects_and_plan.fiscal_year :
    #             self.projects_and_plan_year = self.projects_and_plan.fiscal_year.name
    #         else :
    #             self.projects_and_plan_year = False
    #     else :
    #         self.projects_and_plan_year = False



    @api.onchange('product_id')
    def _set_price(self):
        # self.price_unit = self.product_id.product_tmpl_id.standard_price
        # self.product_uom = self.product_id.product_tmpl_id.uom_id
        self.price_unit = self.product_id.standard_price
        self.standard_price = self.product_id.standard_price
        self.product_uom = self.product_id.uom_id

    @api.model
    def create(self, vals):
        res = super(fw_pfb_FS100Lines, self).create(vals)
        proj_vals = {}
        if res.projects_and_plan:
            line_proj = self.env['fw_pfb_fin_system_100_projects'].search([
                ('fin_id', '=', res.fin_id.id),
                ('projects_and_plan.id', '=', res.projects_and_plan.id)
            ])
            if line_proj:
                if res.fin_id.fin_type != 'eroe' and line_proj.projects_residual_amount < 0 and not line_proj.projects_and_plan.allow_negative:
                    raise ValidationError(_('Budget is not below zero (not allow negative amount)'))
                else:
                    line_proj.projects_reserve += res.price_subtotal
            else:
                current_budget_balance = res.projects_and_plan.budget_balance
                plan_budget_balance = current_budget_balance - res.price_subtotal
                if res.fin_id.fin_type != 'eroe' and  plan_budget_balance < 0 and not res.projects_and_plan.allow_negative:
                    raise ValidationError(_('Budget is not below zero (not allow negative amount)'))
                else:
                    vals = {
                        'fin_id': res.fin_id.id,
                        'projects_and_plan': res.projects_and_plan.id,
                        'projects_reserve': res.price_subtotal,
                    }
                    projects = self.env['fw_pfb_fin_system_100_projects'].create(vals)

        return res


    fin100_state = fields.Selection(STATE_SELECTION,
                             default='draft')

    fin_id = fields.Many2one('fw_pfb_fin_system_100',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)
    product_id = fields.Many2one('product.template',
                                 domain=[('fin_ok', '=', True)],
                                 required=True)
    is_pr_ok = fields.Boolean(related='product_id.pr_ok')
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
    standard_price = fields.Float('Standard Price',
                              store=True,
                              )
    price_subtotal = fields.Float(compute='_compute_subtotal',
                                  string='Subtotal',
                                  readonly=True,
                                  store=True, )
    projects_and_plan = fields.Many2one('account.analytic.account')
    fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        # related='projects_and_plan.fiscal_year',
    )
    year = fields.Char()

    @api.onchange('fiscal_year')
    def _onchange_fiscal_year(self):
        if self.fiscal_year:
            self.year = self.fiscal_year.fiscal_year
            print(self.year)
    # fiscal_year = fields.Many2one('fw_pfb_fin_system_fiscal_year')
    # projects_and_plan = fields.Many2one('account.analytic.account', domain="[('fiscal_year', '=', fiscal_year)]")
    
    price_all_fin401 = fields.Float('Price All Fin401',
                               compute="_compute_price_all_fin401"
                              )

    price_all_fin201 = fields.Float('Price All Fin201',
                              compute="_compute_price_all_fin201"
                              )

    item_fin401_ids = fields.One2many('fin100_line_all_fin401_item','wiz_id',string=_('Request items'))
    item_fin201_ids = fields.One2many('fin100_line_all_fin201_item','wiz_id',string=_('Request items'))


class fw_pfb_FS100RequestToCancelWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_100_request_to_cancel_request'

    memo = fields.Text(
        'Memo',
        required=True
    )

    @api.multi
    def confirm_to_request_to_cancel_fin_100(self):
        context = self._context
        if 'fw_pfb_fin_system_100' == context['active_model']:
            fin100 = self.env['fw_pfb_fin_system_100'].search([
                ('id', '=', context['active_id'])
            ])
            if fin100:
                fin100.is_request_to_cancel = True
                fin100.cancel_reason = self.memo
                # fin100.message_post(
                #     body=_(
                #         "Action : %s <br />Date/Time : %s" % (
                #         "Request To Cancel",
                #         str(fin100.write_date),
                #     ))
                # )
                log_message = fin_middleware.message_log_stamp(self, "Request to Cancel", fin100.write_date)
                fin100.message_post(body=_(log_message))
                # fin100.message_post(body=_("ACTION : Request To Cancel<br /> Message : %s"%(self.memo)))


class fw_pfb_FS100ApproveToCancelWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_100_request_to_cancel'

    def _fin100_cancel_reason(self):
        context = self._context
        # Default reason='-' if fin100 cancel_reason is None
        reason = '-'
        if 'fw_pfb_fin_system_100' == context['active_model']:
            fin100 = self.env['fw_pfb_fin_system_100'].search([
                ('id', '=', context['active_id'])
            ])
            if fin100:
                reason = fin100.cancel_reason
        return reason

    memo = fields.Text('Memo',
                       required=True)
    # Depends cancel_reason from FIN100 to display to wizard
    cancel_reason  = fields.Text(
        default=_fin100_cancel_reason,
        readonly=True,
    )

    @api.multi
    def approve_to_cancel_fin_100(self):
        context = self._context
        if 'fw_pfb_fin_system_100' == context['active_model']:
            fin100 = self.env['fw_pfb_fin_system_100'].search([
                ('id', '=', context['active_id'])
            ])
            if fin100:
                fin100.allowed_to_cancel = True
                # fin100.message_post(
                #     body=_(
                #         "Action : %s <br />Date/Time : %s" % (
                #         "Approve To Cancel",
                #         str(fin100.write_date),
                #     ))
                # )
                log_message = fin_middleware.message_log_stamp(self, "Approve to Cancel", fin100.write_date)
                fin100.message_post(body=_(log_message))
                # fin100.message_post(body=_("ACTION : Approve To Cancel<br /> Message : %s <br /> Time : %s"%(self.memo, self.write_date)))


    @api.multi
    def reject_to_cancel_fin_100(self):
        context = self._context
        if 'fw_pfb_fin_system_100' == context['active_model']:
            fin100 = self.env['fw_pfb_fin_system_100'].search([
                ('id', '=', context['active_id'])
            ])
            if fin100:
                fin100.director_reject = True
                # fin100.message_post(
                #     body=_(
                #         "Action : %s <br />Date/Time : %s" % (
                #         "Reject To Cancel",
                #         str(fin100.write_date),
                #     ))
                # )
                log_message = fin_middleware.message_log_stamp(self, "Reject to Cancel", fin100.write_date)
                fin100.message_post(body=_(log_message))
                # fin100.message_post(body=_("ACTION : Reject To Cancel<br /> Message : %s <br /> Time : %s"%(self.memo, self.write_date)))




class fw_pfb_FS100Approver(models.Model):
    _name = 'fw_pfb_fin_system_100_approver'
    _order = 'position_index asc'

    @api.model
    def _show_fin(self):
        for fin in self:
            fin_user = []

            if fin.state != 'approve' :
                if fin.fin_id.target_approver == fin.approve_position :
                    fin_user.append(fin.employee_user_id.id)

                if fin.approve_position == "SmallNote" :
                    if fin.fin_id.target_approver == "DirectorOfOffice" :
                        fin_user.append(fin.employee_user_id.id)

                if fin.approve_position == "DirectorOfOffice" :
                    if fin.approve_active == True  :
                        canApproveFin = False
                        for checker in fin.fin_id.approver :
                            if checker.approve_active and checker.approve_position != "DirectorOfOffice" :
                                if checker.approve_position == "DirectorOfFinance" or checker.approve_position == "ManagerOfStock" or checker.approve_position == "AssistantOfOffice" or checker.approve_position == "DeputyOfOffice" or checker.approve_position == "SmallNote" :
                                    if checker.state == "approve" :
                                        canApproveFin = True
                        if canApproveFin :
                            fin_user.append(fin.employee_user_id.id)

            if self._uid in fin_user:
                fin.show_fin = True
            else:
                fin.show_fin = False

    @api.depends('fin_position')
    def _is_related_department(self):
        for fin in self:
            if fin.fin_position == 'RelatedGroup':
                fin.is_related_department = True
            else:
                fin.is_related_department = False

    @api.depends('fin_position')
    def _is_not_related_department(self):
        for fin in self:
            if fin.fin_position != 'RelatedGroup':
                fin.is_not_related_department = True
            else:
                fin.is_not_related_department = False

    @api.onchange('employee_line')
    def _onchange_employee_line(self):
        if self.employee_line :
            for i in self.employee_line :
                if i.data_activate :
                    self.employee_id = i.name.id

    @api.onchange('approve_active')
    def _onchange_approve_active(self):
        if self.approve_active :
            self.state = "pending"
        else :
            self.state = False

    @api.onchange('need_to_change_employee')
    def _onchange_need_to_change_employee(self):
        if self.need_to_change_employee :
            if self.fin_position :
                if self.fin_position != "DirectorOfOffice" :
                    if self.fin_position in POSITION_CLASS :
                        list = self.env[ POSITION_CLASS[self.fin_position] ].search([])
                        if list :
                            for i in list :
                                eid = False
                                if self.fin_position != "AssistantOfOfficeSecretary" and self.fin_position != "DeputyOfOfficeSecretary" and  self.fin_position != "DirectorOfOffice" :
                                    eid = i.name.id
                                else :
                                    eid = i.secretary.id

                                self.employee_line += self.employee_line.create( { "name" : eid} )
                else :
                    sid = False
                    hasSettings = self.env['fw_pfb_fin_settings2'].search([], limit=1)
                    if hasSettings :
                        for i in hasSettings :
                            fin = self.env['fw_pfb_fin_settings2'].browse( i.id )
                            if fin :
                                if fin.directorOfOffice :
                                    sid = fin.directorOfOffice.id
                                    self.employee_line += self.employee_line.create( {"name" : sid, "data_activate":True} )
        else :
            self.employee_line = False



    approve_active = fields.Boolean(string='Active')
    position_index = fields.Selection(POSITION_INDEX, string='Approve Position')
    fin_id = fields.Many2one('fw_pfb_fin_system_100',
                             required=True,
                             ondelete='cascade',
                             index=True)
    employee_id = fields.Many2one('hr.employee',
                                  required=True,
                                  domain=[('user_id', '!=', None),
                                          ('fin_can_approve', '=', True)])
    fin_position = fields.Selection(FIN_SELECTION, string='FIN Position')
    approve_position = fields.Selection(APPROVE_POSITION,
                                        string='Approve Position',
                                        required=True)
    employee_user_id = fields.Many2one('res.users',
                                       related='employee_id.user_id',
                                       readonly=True, )
    action_date = fields.Datetime(string='Action Date',
                                  copy=False)
    state = fields.Selection(STATE_APPROVE,
                             string='State approve',
                             default='pending')
    memo = fields.Text(string='Memo',
                       copy=False)
    # real_memo = fields.Text(
    #     string='Memo',
    #     copy=False,
    # )
    show_fin = fields.Boolean(string='Show FIN',
                              compute=_show_fin)
    is_related_department = fields.Boolean(string='Show FIN',
                                           compute=_is_related_department)
    is_not_related_department = fields.Boolean(string='Show FIN',
                                               compute=_is_not_related_department)

    employee_line = fields.One2many('fw_pfb_approve_employee_list', 'release_id', string='Please select employee')

    need_to_change_employee = fields.Boolean(string='Need to change employee', default=False)

    # depends_memo = fields.Boolean(
    #     compute='_memo_depends_fin_position'
    # )

    # @api.depends('fin_position', 'memo')
    # def _memo_depends_fin_position(self):
    #     for line in self:
    #         line.write({
    #             'memo': '-------',
    #         })
            # line.real_memo = line.memo
            # if line.employee_id.user_id.id == self._uid and line.fin_position == 'DirectorOfStrategy':
            #     # Change memo data
            #     line.memo = line.real_memo
            # else:
            #     memo_data = self.env['fw_pfb_fin_system_100_approver'].search([
            #         ('fin_id', '=', line.fin_id.id),
            #         ('fin_position', '=', 'DirectorOfDepartment'),
            #     ])
            #     for memo in memo_data:
            #         for line in self:
            #             if line.id == memo.id:
            #                 line.memo = '---'
                    # memo.memo = 'Test change data'
            # if line.employee_id.user_id.id == self._uid and line.fin_position == 'AssistantOfOffice':


    @api.model
    def create(self, vals):
        vals["need_to_change_employee"] = False
        vals["employee_line"] = False
        return super(fw_pfb_FS100Approver, self).create(vals)

    @api.multi
    def write(self, vals):
        vals["need_to_change_employee"] = False
        vals["employee_line"] = False
        return super(fw_pfb_FS100Approver, self).write(vals)


class fw_pfb_FS100Budget(models.Model):
    _name = 'fw_pfb_fin_system_100_projects'

    @api.depends('projects_reserve', 'projects_residual', 'projects_return')
    def _compute_residual(self):
        for line in self:
            line['projects_residual_amount'] = line.projects_residual - line.projects_reserve + line.projects_return

    fin_id = fields.Many2one('fw_pfb_fin_system_100',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)
    projects_and_plan = fields.Many2one('account.analytic.account',
                                        readonly=True,)

    projects_residual = fields.Float(string='Residual',
                                     related='projects_and_plan.budget_balance',
                                     readonly=True)
    projects_reserve = fields.Float(string='Reserve',
                                    readonly=True)
    projects_return = fields.Float(
        string='Return',
        readonly=True
    )
    projects_residual_amount = fields.Float(string='Residual amount',
                                            compute='_compute_residual',
                                            readonly=True)

class fw_pfb_FS100ApproveWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_100_approver'

    memo = fields.Text('Memo',
                       required=True)

    @api.multi
    def acknowledge_fin_100(self):
        context = self._context
        if context:
            approver_obj = self.env['fw_pfb_fin_system_100_approver'].search([('id', '=', context['active_id'])])
            if approver_obj.state != 'DirectorOfOffice' :
                if approver_obj.approve_position == 'DirectorOfDepartment':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'
                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                        ('approve_active', '=', True),
                        ('approve_position', '=', 'DirectorOfDepartment')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'DirectorOfDepartment')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'DirectorOfDepartment'
                            approver_obj.fin_id.target_approver = 'RelatedGroup'

                elif approver_obj.approve_position == 'RelatedGroup' :
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'RelatedGroup')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'RelatedGroup')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'RelatedGroup'
                            approver_obj.fin_id.target_approver = 'DirectorOfFinance'

                elif approver_obj.approve_position == 'DirectorOfFinance':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'DirectorOfFinance')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'DirectorOfFinance')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'DirectorOfFinance'
                            approver_obj.fin_id.target_approver = 'AssistantOfOffice'



                elif approver_obj.approve_position == 'AssistantOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'AssistantOfOffice')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'AssistantOfOffice')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'AssistantOfOffice'
                            approver_obj.fin_id.target_approver = 'DeputyOfOffice'


                elif approver_obj.approve_position == 'DeputyOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'DeputyOfOffice')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'DeputyOfOffice')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'DeputyOfOffice'
                            approver_obj.fin_id.target_approver = 'SmallNote'

                elif approver_obj.approve_position == 'SmallNote':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'SmallNote'),
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj= self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'SmallNote'),
                        ])

                        if len(check_related_obj) > 0 and approver_obj.fin_id.state != 'SmallNote' :
                            approver_obj.fin_id.state = 'SmallNote'
                            approver_obj.fin_id.target_approver = 'DirectorOfOffice'

                elif approver_obj.approve_position == 'DirectorOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'
                    approver_obj.fin_id.state = 'DirectorOfOffice'
                    approver_obj.fin_id.target_approver = "DirectorOfOffice"

                    if approver_obj.fin_id.fin_lines :
                        for fl in approver_obj.fin_id.fin_lines :
                            fl.write({
                                'fin100_state': 'DirectorOfOffice'
                            })
                else:
                    raise UserError(_('You can not do Approve'))

                if approver_obj.fin_id.target_approver != 'DirectorOfOffice' :
                    list = []
                    targetApprover = approver_obj.fin_id.target_approver
                    for appr in approver_obj.fin_id.approver :
                        if appr.approve_active :
                            if appr.approve_position :
                                astate = appr.approve_position
                                if astate not in list :
                                    list.append( astate )

                    if targetApprover not in list :
                        if targetApprover == "RelatedGroup" :
                            approver_obj.fin_id.target_approver = "DirectorOfFinance"
                            targetApprover = "DirectorOfFinance"

                        if targetApprover not in list :
                            if targetApprover == "DirectorOfFinance" :
                                approver_obj.fin_id.target_approver = "AssistantOfOffice"
                                targetApprover = "AssistantOfOffice"

                        if targetApprover not in list :
                            if targetApprover == "AssistantOfOffice" :
                                approver_obj.fin_id.target_approver = "DeputyOfOffice"
                                targetApprover = "DeputyOfOffice"

                        if targetApprover not in list :
                            if targetApprover == "DeputyOfOffice" :
                                approver_obj.fin_id.target_approver = "SmallNote"
                                targetApprover = "SmallNote"

                        if targetApprover not in list :
                            if targetApprover == "SmallNote" :
                                approver_obj.fin_id.target_approver = "DirectorOfOffice"
                                targetApprover = "DirectorOfOffice"

        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res


    @api.multi
    def approve_fin_100(self):
        context = self._context
        if context:
            approver_obj = self.env['fw_pfb_fin_system_100_approver'].search([('id', '=', context['active_id'])])

            if approver_obj.state != 'DirectorOfOffice' :
                if approver_obj.approve_position == 'DirectorOfDepartment':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'
                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                        ('approve_active', '=', True),
                        ('approve_position', '=', 'DirectorOfDepartment')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'DirectorOfDepartment')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'DirectorOfDepartment'
                            approver_obj.fin_id.target_approver = 'RelatedGroup'

                elif approver_obj.approve_position == 'RelatedGroup' :
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'RelatedGroup')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'RelatedGroup')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'RelatedGroup'
                            approver_obj.fin_id.target_approver = 'DirectorOfFinance'

                elif approver_obj.approve_position == 'DirectorOfFinance':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'DirectorOfFinance')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'DirectorOfFinance')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'DirectorOfFinance'
                            approver_obj.fin_id.target_approver = 'AssistantOfOffice'


                elif approver_obj.approve_position == 'AssistantOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'AssistantOfOffice')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'AssistantOfOffice')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'AssistantOfOffice'
                            approver_obj.fin_id.target_approver = 'DeputyOfOffice'


                elif approver_obj.approve_position == 'DeputyOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'DeputyOfOffice')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'DeputyOfOffice')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'DeputyOfOffice'
                            approver_obj.fin_id.target_approver = 'SmallNote'

                elif approver_obj.approve_position == 'SmallNote':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_100_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'SmallNote'),
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj= self.env['fw_pfb_fin_system_100_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'SmallNote'),
                        ])

                        if len(check_related_obj) > 0 and approver_obj.fin_id.state != 'SmallNote' :
                            approver_obj.fin_id.state = 'SmallNote'
                            approver_obj.fin_id.target_approver = 'DirectorOfOffice'

                elif approver_obj.approve_position == 'DirectorOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'
                    approver_obj.fin_id.state = 'DirectorOfOffice'
                    approver_obj.fin_id.target_approver = "DirectorOfOffice"

                    if approver_obj.fin_id.fin_lines :
                        for fl in approver_obj.fin_id.fin_lines :
                            fl.write({
                                'fin100_state': 'DirectorOfOffice'
                            })
                else:
                    raise UserError(_('You can not do Approve'))

                if approver_obj.fin_id.target_approver != 'DirectorOfOffice' :
                    list = []
                    targetApprover = approver_obj.fin_id.target_approver
                    for appr in approver_obj.fin_id.approver :
                        if appr.approve_active :
                            if appr.approve_position :
                                astate = appr.approve_position
                                if astate not in list :
                                    list.append( astate )

                    if targetApprover not in list :
                        if targetApprover == "RelatedGroup" :
                            approver_obj.fin_id.target_approver = "DirectorOfFinance"
                            targetApprover = "DirectorOfFinance"

                        if targetApprover not in list :
                            if targetApprover == "DirectorOfFinance" :
                                approver_obj.fin_id.target_approver = "AssistantOfOffice"
                                targetApprover = "AssistantOfOffice"

                        if targetApprover not in list :
                            if targetApprover == "AssistantOfOffice" :
                                approver_obj.fin_id.target_approver = "DeputyOfOffice"
                                targetApprover = "DeputyOfOffice"

                        if targetApprover not in list :
                            if targetApprover == "DeputyOfOffice" :
                                approver_obj.fin_id.target_approver = "SmallNote"
                                targetApprover = "SmallNote"

                        if targetApprover not in list :
                            if targetApprover == "SmallNote" :
                                approver_obj.fin_id.target_approver = "DirectorOfOffice"
                                targetApprover = "DirectorOfOffice"

        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res

    @api.multi
    def reject_fin_100(self):
        context = self._context
        if context:
            approver_obj = self.env['fw_pfb_fin_system_100_approver'].search([('id', '=', context['active_id'])])
            approver_obj.memo = self.memo
            # approver_obj.action_date = datetime.now()
            approver_obj.action_date = date.today()
            approver_obj.state = 'reject'
            approver_obj.fin_id.check_reject = True
            approver_obj.fin_id.has_history = True
            approver_obj.fin_id.state = "reject"
            #raise UserError(_('You can not do Reject'))

        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res


# class fw_ksp_pr(models.Model):
#     _inherit = 'fw_ksp_pr'
#
#     @api.model
#     def _get_projects_and_plan(self):
#         proj_id = self._context['projects_and_plan']
#         p_a_p = self.env['budget_system.projects_and_plan'].search([('id', '=', proj_id)], limit=1)
#
#         return p_a_p.id
#
#     fin_id = fields.Many2one('fw_pfb_fin_system_100',
#                              copy=False)
#     budget_request = fields.Float(
#         default=lambda self: self._context['budget_request'] if self._context and 'budget_request' in self._context else None
#     )
#     projects_and_plan = fields.Many2one(
#         'budget_system.projects_and_plan',
#         default=lambda self: self.env['budget_system.projects_and_plan'].search([('id', '=', 1207)], limit=1)
#     )

class fw_pfb_approve_employee_list(models.TransientModel):
    _name = 'fw_pfb_approve_employee_list'

    release_id = fields.Many2one('fw_pfb_fin_system_100_approver')

    data_activate = fields.Boolean(string='Active')
    name = fields.Many2one('hr.employee', string='Employee Name')


# class pfb_FS100CreatePRWizard(models.TransientModel):
#     _name = 'wizard.fin_system_100_create_pr'
#
#     pr_name = fields.Char(
#             string="PR name",
#     )
#     pr_ids = fields.Many2one(
#             string="PR ids",
#     )
#
#     def create_pr(self):
#         print("Create PR From Wizard !!")
    

    # def _fin100_cancel_reason(self):
    #     context = self._context
    #     # Default reason='-' if fin100 cancel_reason is None
    #     reason = '-'
    #     if 'fw_pfb_fin_system_100' == context['active_model']:
    #         fin100 = self.env['fw_pfb_fin_system_100'].search([
    #             ('id', '=', context['active_id'])
    #         ])
    #         if fin100:
    #             reason = fin100.cancel_reason
    #     return reason
    #
    # memo = fields.Text('Memo',
    #                    required=True)
    # # Depends cancel_reason from FIN100 to display to wizard
    # cancel_reason  = fields.Text(
    #     default=_fin100_cancel_reason,
    #     readonly=True,
    # )
    #
    # @api.multi
    # def approve_to_cancel_fin_100(self):
    #     context = self._context
    #     if 'fw_pfb_fin_system_100' == context['active_model']:
    #         fin100 = self.env['fw_pfb_fin_system_100'].search([
    #             ('id', '=', context['active_id'])
    #         ])
    #         if fin100:
    #             fin100.allowed_to_cancel = True
    #             # fin100.message_post(
    #             #     body=_(
    #             #         "Action : %s <br />Date/Time : %s" % (
    #             #         "Approve To Cancel",
    #             #         str(fin100.write_date),
    #             #     ))
    #             # )
    #             log_message = fin_middleware.message_log_stamp(self, "Approve to Cancel", fin100.write_date)
    #             fin100.message_post(body=_(log_message))
    #             # fin100.message_post(body=_("ACTION : Approve To Cancel<br /> Message : %s <br /> Time : %s"%(self.memo, self.write_date)))
    #
    #
    # @api.multi
    # def reject_to_cancel_fin_100(self):
    #     context = self._context
    #     if 'fw_pfb_fin_system_100' == context['active_model']:
    #         fin100 = self.env['fw_pfb_fin_system_100'].search([
    #             ('id', '=', context['active_id'])
    #         ])
    #         if fin100:
    #             fin100.director_reject = True
    #             # fin100.message_post( #     body=_(
    #             #         "Action : %s <br />Date/Time : %s" % (
    #             #         "Reject To Cancel",
    #             #         str(fin100.write_date),
    #             #     ))
    #             # )
    #             log_message = fin_middleware.message_log_stamp(self, "Reject to Cancel", fin100.write_date)
    #             fin100.message_post(body=_(log_message))
    #
