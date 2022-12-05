# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from lxml import etree
from . import fin_middleware

DUMMY_EMPLOYEE = 4596
DEV_DUMMY_EMPLOYEE = 4595

FIN_TYPE = [('lr', 'Loan request')]

PRIORITY = [('1_normal', 'Normal'),
                   ('0_urgent', 'Urgent')]

POSITION_INDEX = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),
                  (11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20)]
                  
FIN_TYPE_ON_FIN100 = [('eroe', 'Expense request of express'),
                   ('erob', 'Expense request of budget'),
                   ('proo', 'Purchase reguest of objective')]

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
                    ('AssistantOfOffice', 'Executive Vice President'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),
                    ('SmallNote', 'Small Note'),
                    ('DirectorOfOffice', 'Director'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                    ('reject', 'Reject')]

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

APPROVE_POSITION = [('DirectorOfDepartment', 'Vice President/Director'),
                    ('RelatedGroup', 'Related Group'),
                    ('DirectorOfFinance', 'Division Manager of Finance, Accounting and Control Division'),
                    ('ManagerOfStock', 'Division Manager of General Affairs and Facilities Division'),
                    ('AssistantOfOffice', 'Executive Vice President'),
                    ('DeputyOfOffice', 'Senior Executive Vice President'),
                    ('SmallNote', 'Small Note'),
                    ('DirectorOfOffice', 'President/CEO')]

STATE_APPROVE = [('pending', 'Pending'),
                 ('approve', 'Approve'),
                 ('reject', 'Reject')]

STATE_RESIDUAL = [('no_residual', 'No Residual'), ('residual', 'Residual')]


class fw_pfb_FS401(models.Model):
    _name = 'fw_pfb_fin_system_401'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority ASC, fin_date DESC, fin_no DESC'

    def date_by_adding_business_days(self, from_date, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:
                continue
            business_days_to_add -= 1
        return current_date

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
            approver = self.env['fw_pfb_fin_system_401_approver'].search(
                [('fin_id', '=', self.id), ('employee_user_id.id', '=', self._uid)])
            if len(approver) > 1:
                for ap in approver:
                    rights += ap.fin_position + ' , '
            else:
                rights = approver.fin_position

        else:
            rights = 'fin_user'
        self.approver_rights = rights
        if rights == 'director':
            self.is_director = True

    @api.depends('requester')
    def _check_is_requester(self):
        for rec in self:
            if rec._uid == rec.requester.user_id.id:
                rec.is_requester = True
            else:
                rec.is_requester = False

    @api.depends('canedit_financial')
    def _is_canedit_financial(self):
        self.canedit_financial = False
        usrid = self._uid
        group_id = self.env['res.groups'].search([('name', 'like', 'Can Edit Financial Staff Verification')], limit=1)
        if group_id :
            if group_id.users :
                for i in group_id.users :
                    if i.id == usrid :
                        self.canedit_financial = True
    
    @api.returns('self')
    def _is_canedit_financial_default(self):
        canedit_financial = False
        usrid = self._uid
        group_id = self.env['res.groups'].search([('name', 'like', 'Can Edit Financial Staff Verification')], limit=1)
        if group_id :
            if group_id.users :
                for i in group_id.users :
                    if i.id == usrid :
                        canedit_financial = True
        
        return canedit_financial
            
        

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

    
    @api.onchange('flow_template')
    def _onchange_flow_template(self):
        self.approver = False
        id =  self.flow_template.id
        
        flow = self.env['fw_pfb_flow_template'].browse( id )
        if flow :
            if flow.approve_line :
                for line in flow.approve_line :
                    data = {
                            "employee_id" : line.emp_name.id,
                            "fin_position" : line.position,
                            "approve_active" : line.data_activate,
                            "approve_position" : line.approve_position,
                            "position_index" : line.position_index
                        }
                    if line.data_activate :
                        data["state"] = "pending"
                    self.approver += self.approver.new( data )
                    
    # Fin system

    priority = fields.Selection(PRIORITY, string='Priority', required=True)
    
    target_approver = fields.Char(string='Target Approver' )

    flow_template = fields.Many2one('fw_pfb_flow_template',
                                domain=[('type', '=', 'lr'),('data_activate', '=', True)],
                                string='Flow Template')

    fin_objective = fields.Many2one('fw_pfb_objective',
                                 string='Objective')
    fin_type = fields.Selection(FIN_TYPE, string='FIN Type', default="lr")

    participantas_quantity = fields.Char(string='Participantas Quantity', default="0")
    place = fields.Many2many("ir.attachment",
                                  "attachment_fin401_place_rel",
                                  "attachment_fin401_place_id",
                                  "attachment_id",
                                  string="Place")
    operation_date = fields.Many2many("ir.attachment",
                                  "attachment_fin401_operation_date_rel",
                                  "attachment_fin401_operation_date_id",
                                  "attachment_id",
                                  string="Operation Date")
    seminar_partcipants = fields.Many2many("ir.attachment",
                                  "attachment_fin401_seminar_rel",
                                  "attachment_fin401_seminar_id",
                                  "attachment_id",
                                  string="Seminar Partcipants")
    other = fields.Text(string='Other')
    estimate_output = fields.Text(string='Estimate')
    please_consider = fields.Selection(FIN_TYPE, string='Please Consider', default="lr")

    canedit_financial = fields.Boolean(string='Can Edit Financial Staff Verification',
                                  compute='_is_canedit_financial',
                                    default=_is_canedit_financial_default)
    fin_no = fields.Char(string='fin NO.', readonly=True )
    
    fin_date = fields.Date(string='fin Date',
                           default=lambda self: date.today(),
                           readonly=True)
    fin_end_date = fields.Date(string='fin End Date')
    requester = fields.Many2one('hr.employee',
                                string='Requester',
                                default=_default_employee_get)
    is_requester = fields.Boolean(string='Is requester',
                                  compute='_check_is_requester')
    is_director = fields.Boolean(string="Is director",
                                 compute='_get_approver_rights')
    department = fields.Many2one('hr.department',
                                 string='Department',
                                 related='requester.department_id',)
    actual_department_name = fields.Char(string='Department',
                                         compute='_set_actual_department_name',)
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
    participants = fields.Many2many('hr.employee')
    template_id = fields.Many2many('sale.order.template',
                                   'so_template_fin_rel',
                                   'so_id',
                                   'fin_id',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]},
                                   domain=[('fin_ok', '=', True)])
    fin_lines = fields.One2many('fw_pfb_fin_system_401_line',
                                'fin_id',
                                copy=True, )
    is_fin_lock = fields.Boolean(string="Lock")
    fin_ref = fields.Char(string='Reference')
    fin_remark = fields.Text(string='Remark')
    price_total = fields.Float(string='Total', compute='_compute_total')
    approver = fields.One2many('fw_pfb_fin_system_401_approver',
                               'fin_id',
                               copy=True)
    approver_rights = fields.Char(string='Approver Rights',
                                  compute="_get_approver_rights")
    can_cancel = fields.Boolean(string='Can cancel',
                                compute='_check_can_cancel')
    show_fin = fields.Boolean(string='Show FIN', )
    check_reject = fields.Boolean(string='Check Reject')
    attachment = fields.Many2many("ir.attachment",
                                  "attachment_fin401_rel",
                                  "attachment_fin401_id",
                                  "attachment_id",
                                  string="Attachment")

    activity_end_date = fields.Date(string='Activity End Date', required=True)
    loan_period = fields.Selection(
        [('7days_from_activity_end_date', '7 Business Days From Activity End date '),
        ('7days_from_activity_end_date_domestic', '7 Business Days From Activity End date For Work Domestic'),
        ('15days_from_activity_end_date_oversea', '15 Business Days From Activity End date For Work Overseas')],
        string='Loan period',
        required=True,
    )
    loan_residual_selection = fields.Selection(STATE_RESIDUAL, string='Loan Residual Selection')
    loan_residual_amount = fields.Float(string='Residual amount')
    loan_residual_reason = fields.Text(string='Residual Reason')
    bank_transfer_branch = fields.Char(string='Bank branch')
    bank_transfer_account = fields.Char(string='Account ID')

    fin_staff_loan_residual_selection = fields.Selection(STATE_RESIDUAL, string='Fin staff loan residual selection')
    fin_staff_loan_residual_amount = fields.Float(string='Residual amount')
    fin_staff_employee = fields.Many2one('hr.employee',
                                   string='Financial Staff')
    fin_staff_verify_date = fields.Date(string='Verify Date')

    swap = fields.Boolean(string="Swap", default=False)

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

    @api.multi
    def _can_approve_to_cancel(self):
        director_id = []
        for obj in self:
            director = self.env['fw_pfb_fin_settings2'].sudo().search([])
            for directoroffice in director.directorOfOffice.user_id:
                director_id.append(directoroffice.id)
            if self._uid in director_id:
                obj.can_approve_to_cancel = True

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, fin_date=date.today())
        return super(fw_pfb_FS401, self).copy(default)

    @api.multi
    def _set_actual_department_name(self):
        for record in self:
            record.actual_department_name = record.department.name

    @api.onchange('activity_end_date', 'loan_period')
    def _onchange_activity_period(self):
        day_count = 0
        if self.loan_period == '7days_from_activity_end_date' or self.loan_period == '7days_from_activity_end_date_domestic':
            day_count = 7
        elif self.loan_period == '15days_from_activity_end_date_oversea':
            day_count = 15
        if self.activity_end_date:
            self.fin_end_date = self.date_by_adding_business_days(datetime.strptime(str(self.activity_end_date), '%Y-%m-%d').date(), day_count)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_fin = self.env['fw_pfb_fin_system_401']
        env_fin_approver = self.env['fw_pfb_fin_system_401_approver']
        params = self._context.get('params')

        checkRule = False

        if params :
            if "action" in params :
               if params["action"] == 1125 :
                   checkRule = True
        
        res = super(fw_pfb_FS401, self).fields_view_get(
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
    def name_get(self):
        return [(cat.id, cat.fin_no) for cat in self]

    @api.model
    def create(self, vals):
        vals['fin_no'] = self.env['ir.sequence'].next_by_code('seq_fw_pfb_fin_401')
        if "approver" in vals :
            for ap in vals["approver"] :
                if len(ap) == 3 :
                    datas = ap[2]
                    if "approve_active" in datas :
                        if datas["approve_active"] == True :
                            if "employee_id" in datas :
                                if "employee_id" in datas:
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
        res = super(fw_pfb_FS401, self).create(vals)

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
        # res.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Create FIN401",
        #         str(res.create_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "Create FIN401", res.create_date)
        res.message_post(body=_(log_message))

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

        return True

    @api.multi
    def fin_complete(self):
        self.write({
            'state': 'completed',
            'target_approver' : False
        })

        items = self.env["fin100_line_all_fin401_item"].search([("fin401_id", "=", str(self.id) )])
        if items :
            for item in items :
                item.write({"status" : "completed"})

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
        #         "Complete FIN401",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "Complete FIN401", self.write_date)
        self.message_post(body=_(log_message))

        return True

    @api.multi
    def fin_request_to_cancel(self):
        self.write({
            'is_request_to_cancel': True,
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
        log_message = fin_middleware.message_log_stamp(self, "Approve to Cancel", self.create_date)
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

        items = self.env["fin100_line_all_fin401_item"].search([("fin401_id", "=", str(self.id) )])
        if items :
            for item in items :
                item.write({"status" : "cancelled"})
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
        #         "FIN401 Cancel",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "FIN401 Cancel", self.write_date)
        self.message_post(body=_(log_message))

        return True

    @api.multi
    def fin_set_to_draft(self):

        self.fin_date = date.today()
        self.can_approve_to_cancel = False
        self.allowed_to_cancel = False
        self.is_request_to_cancel = False

        for approver in self.approver:
            approver.write({
                'memo': '',
                'action_date': None,
                'state': 'pending',
            })
        self.write({
            'state': 'draft',
            'target_approver' : False,
            'check_reject': False,
        })

        items = self.env["fin100_line_all_fin401_item"].search([("fin401_id", "=", str(self.id) )])
        if items :
            for item in items :
                item.write({"status" : "draft"})

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
        #         "FIN401 Lock",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "FIN401 Lock", self.write_date)
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
        #         "FIN401 Unlock",
        #         str(self.write_date),
        #     ))
        # )
        log_message = fin_middleware.message_log_stamp(self, "FIN401 Unlock", self.write_date)
        self.message_post(body=_(log_message))

        return True

    @api.multi
    def button_request_fin100(self):
        print('CREATE Wizard')
        # create wizard
        self.write({})
        newid = self.env['fin_100_request_wiz'].create({})
        return {
                'name': "FIN100 Requests",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fin_100_request_wiz',
                'view_id': self.env.ref('fin_system.fin_100_request_wiz_form').id,
                'res_id':newid.id,
                'type': 'ir.actions.act_window',
                'target': 'new'
          }

    @api.multi
    def swapFIN401_dummy(self):
        return True

    @api.multi
    def swapFIN401(self):
        f401_lines = self.env['fw_pfb_fin_system_401_line'].search([ ( 'fin_id', '=', self.id ) ])
        if f401_lines :
            for line in f401_lines :
                if line.fin_line_id :
                    data2 = {
                            "wiz_id" : line.fin_line_id,
                            "fin_date" : self.fin_date,
                            "fin401_id" : str( self.id ),
                            "fin401_line_id" : line.id,
                            "product_id" : line.product_id.id,
                            "description" : line.description,
                            "status" : self.state
                        }
                    fin100_line_id = self.env['fw_pfb_fin_system_100_line'].browse( int( line.fin_line_id ) )
                    if fin100_line_id :
                        fin100_line_id.item_fin401_ids.create( data2 )

                        data = {
                            "price_unit" : fin100_line_id.price_unit,
                            "product_uom_qty" : fin100_line_id.product_uom_qty,
                            "product_uom" : fin100_line_id.product_uom.id,
                            "price_subtotal" : fin100_line_id.price_subtotal
                        }

                        if int( line.price_subtotal ) != 0:
                            data["lend"] = line.price_subtotal

                        line.write( data )
        

        self.write({
            'swap': True
        })

        return True


    @api.multi
    @api.depends('fin_lines.price_subtotal')
    def _compute_total(self):
        for fin in self:
            total = 0
            for line in fin.fin_lines:
                total += line.price_subtotal
            fin.price_total = total

    @api.onchange('template_id')
    def _onchange_template(self):
        new_lines = []
        for tp_id in self.template_id:
            quote_template = self.env['sale.order.template.line'].sudo().search([('sale_order_template_id', '=', tp_id.id)])
            for quote_line in quote_template:
                new_lines.append((0, 0, {
                    'product_id': quote_line.product_id.id,
                    'description': quote_line.name,
                    'price_unit': quote_line.price_unit,
                    'product_uom_qty': quote_line.product_uom_qty,
                    'product_uom': quote_line.product_uom_id.id,
                }))
        self.fin_lines = new_lines


class fw_pfb_FS401Lines(models.Model):
    _name = 'fw_pfb_fin_system_401_line'

    @api.one
    def _compute_price_all_fin201(self):
        for rec in self :
            total = 0
            lines = self.env["fw_pfb_fin_system_201_line"].search( [("fin_line_id", "=", rec.fin_line_id )] )
            if lines :
                for line in lines :
                    total += line.pay_amount
                
                rec.price_all_fin201 = total

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_subtotal(self):
        for line in self:
            line['price_subtotal'] = line.product_uom_qty * line.price_unit

    @api.onchange('product_id')
    def _set_price(self):
        # self.price_unit = self.product_id.product_tmpl_id.standard_price
        # self.product_uom = self.product_id.product_tmpl_id.uom_id
        self.price_unit = self.product_id.standard_price
        self.product_uom = self.product_id.uom_id

    fin_type = fields.Selection(FIN_TYPE_ON_FIN100, string='FIN Type')

    fin_id = fields.Many2one('fw_pfb_fin_system_401',
                             required=True,
                             ondelete='cascade',
                             index=True,
                             copy=False)
    fin_line_id = fields.Char(string='Fin line id' )
    fin100_id = fields.Many2one('fw_pfb_fin_system_100',string=_("Fin100 number"))
    product_id = fields.Many2one('product.template',
                                 domain=[('fin_ok', '=', True)])
    description = fields.Char(string='description', )
    product_uom_qty = fields.Float(string='Quantity',
                                   # digits=dp.get_precision('Product Unit of Measure'),
                                   default=1.0)
    product_uom = fields.Many2one('uom.uom',
                                  string='Unit of Measure',
                                  store=True,)
                                  # related='product_id.product_tmpl_id.uom_id',
    price_unit = fields.Float('Unit Price',
                              # digits=dp.get_precision('Product Price'),
                              store=True,
                              # default=_default_price,
                              # default='product_id.lst_price',
                              )
    price_subtotal = fields.Float(compute='_compute_subtotal',
                                  string='Subtotal',
                                  readonly=True,
                                  store=True, )
    projects_and_plan = fields.Many2one('account.analytic.account')

    lend =  fields.Float('Lend Total', default = 0)

    price_all_fin201 = fields.Float('Price All Fin201', compute="_compute_price_all_fin201")

    @api.multi
    def unlink(self):
        for rec in self :
            strId = str(rec.id)
            lineF401 = self.env["fin100_line_all_fin401_item"].search([("fin401_line_id", "=" , strId )])
            if lineF401 : 
                lineF401.unlink()

            return super(fw_pfb_FS401Lines, self).unlink()


class fw_pfb_FS401RequestToCancelWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_401_request_to_cancel_request'

    memo = fields.Text(
        'Memo',
        required=True
    )

    @api.multi
    def confirm_to_request_to_cancel_fin_401(self):
        context = self._context
        if 'fw_pfb_fin_system_401' == context['active_model']:
            fin401 = self.env['fw_pfb_fin_system_401'].search([
                ('id', '=', context['active_id'])
            ])
            if fin401:
                fin401.is_request_to_cancel = True
                fin401.cancel_reason = self.memo
                # fin401.message_post(
                #     body=_(
                #         "Action : %s <br />Date/Time : %s" % (
                #         "Request To Cancel",
                #         str(fin401.write_date),
                #     ))
                # )
                log_message = fin_middleware.message_log_stamp(self, "Request To Cancel", fin401.write_date)
                fin401.message_post(body=_(log_message))
                # fin100.message_post(body=_("ACTION : Request To Cancel<br /> Message : %s"%(self.memo)))


class fw_pfb_FS401ApproveToCancelWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_401_approve_to_cancel'

    memo = fields.Text('Memo',
                       required=True)

    @api.multi
    def approve_to_cancel_fin_401(self):
        context = self._context
        print(context['active_id'])
        if 'fw_pfb_fin_system_401' == context['active_model']:
            fin401 = self.env['fw_pfb_fin_system_401'].search([
                ('id', '=', context['active_id'])
            ])
            if fin401:
                fin401.allowed_to_cancel = True
                # fin401.message_post(
                #     body=_(
                #         "Action : %s <br />Date/Time : %s" % (
                #         "Approve To Cancel",
                #         str(fin401.write_date),
                #     ))
                # )
                log_message = fin_middleware.message_log_stamp(self, "Approve To Cancel", fin401.write_date)
                fin401.message_post(body=_(log_message))


    @api.multi
    def reject_to_cancel_fin_401(self):
        context = self._context
        if 'fw_pfb_fin_system_401' == context['active_model']:
            fin401 = self.env['fw_pfb_fin_system_401'].search([
                ('id', '=', context['active_id'])
            ])
            if fin401:
                fin401.director_reject = True
                # fin401.message_post(
                #     body=_(
                #         "Action : %s <br />Date/Time : %s" % (
                #         "Reject To Cancel",
                #         str(fin401.write_date),
                #     ))
                # )
                log_message = fin_middleware.message_log_stamp(self, "Reject To Cancel", fin401.write_date)
                fin401.message_post(body=_(log_message))


class fw_pfb_FS401Approver(models.Model):
    _name = 'fw_pfb_fin_system_401_approver'
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
    approve_position = fields.Selection(APPROVE_POSITION, string='Approve Position', required=True)
    employee_line = fields.One2many('fw_pfb_approve_employee_list401', 'release_id', string='Please select employee')
    need_to_change_employee = fields.Boolean(string='Need to change employee', default=False)

    fin_id = fields.Many2one('fw_pfb_fin_system_401',
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
    show_fin = fields.Boolean(string='Show FIN',
                              compute=_show_fin)

    @api.model
    def create(self, vals):
        vals["need_to_change_employee"] = False
        vals["employee_line"] = False
        return super(fw_pfb_FS401Approver, self).create(vals)

    @api.multi
    def write(self, vals):
        vals["need_to_change_employee"] = False
        vals["employee_line"] = False
        return super(fw_pfb_FS401Approver, self).write(vals)



class fw_pfb_FS401ApproveWizard(models.TransientModel):
    _name = 'wizard.fw_pfb_fin_system_401_approver'

    memo = fields.Text('Memo', required=True)

    @api.multi
    def approve_fin_401(self):
        context = self._context
        if context:
            approver_obj = self.env['fw_pfb_fin_system_401_approver'].search([('id', '=', context['active_id'])])
            if approver_obj.state != 'DirectorOfOffice' : 
                if approver_obj.approve_position == 'DirectorOfDepartment':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'
                    related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                        ('approve_active', '=', True),
                        ('approve_position', '=', 'DirectorOfDepartment')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
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

                    related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'RelatedGroup')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                            ('fin_id', '=', approver_obj.fin_id.id),
                            ('state', '=', 'approve'),
                            ('approve_active', '=', True),
                            ('approve_position', '=', 'RelatedGroup')
                        ])

                        if len(related_obj) == len(check_related_obj):
                            approver_obj.fin_id.state = 'RelatedGroup'
                            approver_obj.fin_id.target_approver = 'AssistantOfOffice'                
                
                elif approver_obj.approve_position == 'AssistantOfOffice':
                    approver_obj.memo = self.memo
                    approver_obj.action_date = datetime.now()
                    approver_obj.state = 'approve'

                    related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'AssistantOfOffice')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
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

                    related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'DeputyOfOffice')
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
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

                    related_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approver_obj.fin_id.id),
                            ('approve_active', '=', True),
                        ('approve_position', '=', 'SmallNote'),
                    ])

                    if len(related_obj) >= 1:
                        check_related_obj= self.env['fw_pfb_fin_system_401_approver'].search([
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
                        if targetApprover not in list :
                            if targetApprover == "RelatedGroup" :
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
    def reject_fin_401(self):
        context = self._context
        if context:
            approver_obj = self.env['fw_pfb_fin_system_401_approver'].search([('id', '=', context['active_id'])])
            approver_obj.memo = self.memo
            approver_obj.action_date = datetime.now()
            approver_obj.state = 'reject'
            approver_obj.fin_id.check_reject = True
            approver_obj.fin_id.state = "reject"
            #raise UserError(_('You can not do Reject'))
        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res

class fw_pfb_approve_employee_list(models.TransientModel):
    _name = 'fw_pfb_approve_employee_list401'

    release_id = fields.Many2one('fw_pfb_fin_system_401_approver')

    data_activate = fields.Boolean(string='Active')
    name = fields.Many2one('hr.employee', string='Employee Name')
