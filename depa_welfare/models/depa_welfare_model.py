# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

FIN_100_READY_STATUS = 'completed'
FAMILY_RELATIONS = [
    ('children', 'บุตร'),
    ('parent', 'บิดา-มารดา'),
    ('spouse', 'คู่สมรส')
]
EXPENSE_FOR = [
    ('self', 'ตนเอง'),
    ('family', 'บุคคลในครอบครัว')
]
WELFARE_STATE = [
    ('draft', 'Draft'),
    # ('sent', 'Sent'),
    ('DocumentInspector', 'Inspect'),
    ('ManagerOfHr', 'Head of Human Resource'),
    ('DirectorOfDepartment', 'Vice President/Director'),
    ('HeadOfFinance', 'Head of Finance and Accounting'),
    ('ManagerOfFinance', 'Manager of Finance and Accounting'),
    # ('SmallNote', 'Small Note'),
    ('DirectorOfOffice', 'Director'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('reject', 'Reject')
]


class depa_welfare(models.Model):
    _name = 'depa_welfare'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_info(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ])
        return employee

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        # print(fiscal_year_obj)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    def _get_my_point(self):
        # print(self)
        employee_point = self.env['depa_welfare_hr_lines'].search([
            ('employee_id', '=', self._get_employee_info().id),
            ('hr_employee_id.year', '=', self._default_fiscal_year())
        ], limit=1)

        if employee_point:
            return round(employee_point.point, 2)

    def _get_workflow_state(self):
        state = False
        flow_using = self.env['depa_welfare_flow_setting'].search([
            ('is_used', '=', True)
        ], limit=1)

        if flow_using:
            dicts = [{"step": int(line.step),"code":line.state.code, "name":line.state.name} for line in flow_using.workflow_process_ids]
            flow_sorted = sorted(dicts, key=lambda item: item["step"])
            state = [(line["code"], line["name"]) for line in flow_sorted]

        return state


    # def _get_my_point_amount(self):
    #     if self._get_my_point():
    #         return self._get_my_point() * 105


    wel_no = fields.Char()
    fin_no = fields.Many2one(
        "fw_pfb_fin_system_100",
        string='อ้างอิง FIN100',
        compute="_get_fin_no",
        store=True,
    )
    fin201_no = fields.Many2one(
        "fw_pfb_fin_system_201",
        string='อ้างอิง FIN201',
    )
    welfare_owner = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )
    employee_id = fields.Many2one(
        'hr.employee',
        default=lambda self: self._get_employee_info().id
    )
    emp_code = fields.Char(
        string='รหัสพนักงาน',
        default=lambda self: self._get_employee_info().emp_code
    )
    emp_name =  fields.Char(
        string='ชื่อ-นามสกุล',
        default=lambda self: self._get_employee_info().name
    )
    emp_dept_name = fields.Char(
        string='สังกัด',
        default=lambda self: self._get_employee_info().department_id.name
    )
    is_emp_gbdi = fields.Boolean(
        default=lambda self: self._get_employee_info().department_id.is_gbdi
    )
    point_balance = fields.Float(
        string='คะแนนคงเหลือ',
        default=_get_my_point
    )
    amount_balance = fields.Float(
        string='จำนวนเงินคงเหลือ',
        compute="_depends_amount_balance",
        store=True,
    )
    expense_for = fields.Selection(
        EXPENSE_FOR,
        string='Expense For',
        default='self'
    )
    expense_for_self = fields.Boolean()
    expense_for_family = fields.Boolean()
    family_name = fields.Char()
    family_relation = fields.Selection(
        FAMILY_RELATIONS,
        'Family Relation'
    )
    depa_welfare_lines_ids = fields.One2many(
        "depa_welfare_lines",
        "depa_welfare_lines_id",
        # ondelete="cascade",
        required=True,
        copy=True
    )
    depa_welfare_approval_lines_ids = fields.One2many(
        "depa_welfare_approval_lines",
        "depa_welfare_approval_lines_id",
        # ondelete="cascade",
        required=True,
        copy=True
    )
    amount_total = fields.Float(
        string='จำนวนเงินที่เบิกตามสิทธิ์',
        compute="_amount_total",
        store=True,
        readonly=True,
    )
    amount_total_fund = fields.Float(
        string='จำนวนเงินที่จ่ายพนักงาน',
        compute="_amount_total",
        store=True,
        readonly=True,
    )
    fund = fields.Boolean(
        default=False
    )
    point_total = fields.Float(
        string='คะแนนที่ใช้',
        compute="_point_total",
        store=True,
        readonly=True,
    )
    welfare_year = fields.Char(
        string='ปีงบประมาณ',
        compute='_depends_welfare_year',
        store=True,
    )
    welfare_round = fields.Integer(
        string='รอบการเบิกที่',
        compute='_depends_welfare_round',
        store=True,

    )
    welfare_round_start = fields.Date(
        string='วันที่เริ่มต้น',
        # readonly=True,
    )
    welfare_round_end = fields.Date(
        string='วันที่สิ้นสุด',
        # readonly=True,
    )
    welfare_state = fields.Selection(
        WELFARE_STATE,
        default='draft'
    )
    welfare_document_date = fields.Date(
        string='วันที่เอกสาร',
        default=lambda self: date.today()
        # readonly=True,
    )
    welfare_fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        string='ปีงบประมาณ',
        # readonly=True,
    )
    state_approval = fields.Many2one(
        'hr.employee'
    )
    state = fields.Selection(
        _get_workflow_state,
        default='draft',
        string='สถานะ',
    )
    prev_state = fields.Char()
    next_state = fields.Char()


    no_ce = fields.Html(
        string='no_create_edit',
        sanitize=False,
        compute='_compute_no_ce_css',
        store=False,
    )
    current_user = fields.Many2one(
        'res.users',
        compute='_get_current_user',
        store=False
    )
    show_button_make_approval = fields.Boolean(
        'Show Make Approval',
        compute='_compute_show_button_make_approval',
        store = False
    )
    show_button_resend_to_inspector = fields.Boolean(
        'Show Resend Inspector',
        compute='_compute_show_button_resend_to_inspector',
        store=False
    )
    point_remain = fields.Float(
        string="คะแนนคงเหลือ",
        compute="_point_remain",
        store=True,
        readonly=True
    )
    amount_remain = fields.Float(
        string="จำนวนเงินคงเหลือ",
        compute="_amount_remain",
        store=True,
        readonly=True
    )

    @api.depends('point_total', 'point_balance')
    def _point_remain(self):
        for rec in self:
            rec.point_remain = rec.point_balance - round(rec.point_total, 2)

    @api.depends('amount_total')
    def _amount_remain(self):
        for rec in self:
            rec.amount_remain = rec.amount_balance - rec.amount_total

    @api.multi
    def name_get(self):
        return [(rec.id, rec.wel_no) for i, rec in enumerate(self)]

    @api.depends('welfare_fiscal_year')
    def _get_fin_no(self):
        # print(self)
        for rec in self:
            fin_100 = self.env['fw_pfb_fin_system_100'].search([
                ('is_welfare', '=', True),
                ('welfare_round', '=', rec.welfare_round),
                ('fiscal_year.fiscal_year', '=', rec.welfare_year),
                ('state', '=', FIN_100_READY_STATUS),    
            ], 
            limit=1,
            order='create_date desc'
            )
            if fin_100:
                rec.fin_no = fin_100.id
            else:
                rec.fin_no = False

    @api.depends('state')
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user

    @api.depends('state')
    def _compute_show_button_make_approval(self):
        for rec in self:
            if self.env.user == rec.state_approval.user_id:
                rec.show_button_make_approval = True
            elif self.env.user == rec.welfare_owner:
                rec.show_button_make_approval = False

    @api.depends('state')
    def _compute_show_button_resend_to_inspector(self):
        for rec in self:
            if rec.state == 'adjust' and self.env.user == rec.welfare_owner:
                rec.show_button_resend_to_inspector = True
            else:
                rec.show_button_resend_to_inspector = False

    # welfare_document_state = fields.Char(
    #     default='draft'
    # )
    # @api.model
    # def default_get(self, fields):
    #     res = super(depa_welfare, self).default_get(fields)
    #     print("test...")
    #     return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(depa_welfare, self).fields_view_get(
                    view_id=view_id,
                    view_type=view_type,
                    toolbar=toolbar,
                    submenu=submenu
        )

        if view_type == 'form':
            print(self.env.user.id)
            current_usr = self.env.user.id
            welfares = self.env['depa_welfare'].search([
                ('state', '=', 'draft'),
                ('create_uid', '=', current_usr)
            ])

            for welfare in welfares:
                # welfare.fin_no = 'TestingFin100NO.X'
                fin_100 = self.env['fw_pfb_fin_system_100'].search([
                    ('is_welfare', '=', True),
                    ('welfare_round', '=', welfare.welfare_round),
                    ('fiscal_year.fiscal_year', '=', welfare.welfare_year),
                    ('state', '=', FIN_100_READY_STATUS),
                ], limit=1)
                if fin_100:
                    welfare.fin_no = fin_100.id
                else:
                    welfare.fin_no = False

                welfare.point_balance = self._get_my_point()

        return res

    @api.model
    def default_get(self, fields_list):
        step = 0
        res = super(depa_welfare, self).default_get(fields_list)
        flow_using = self.env['depa_welfare_flow_setting'].search([
            ('is_used', '=', True)
        ], limit=1)
        approvals = []
        if flow_using:
            flow_using = self.env['workflow_process_setting'].search([
                ('workflow_process_id', '=', flow_using.id)
            ], order="step asc")
            for i, process in enumerate(flow_using): #Add default approval flow
                if process.is_approve_required:
                    step += 1
                    approvals.append(
                        (
                            0,
                            0,
                            {
                                'process_setting_id': process.id,
                                'process_step': int(step),
                                'process_approval': process.approve.id,
                                'process_approval_position': process.approve.job_id.name
                            }
                         )
                    )

        res.update({'depa_welfare_approval_lines_ids': approvals})
        return res

    @api.depends('state')
    def _compute_no_ce_css(self):
        # print(self)
        for application in self:
            # Modify below condition
            if application.state != 'draft':
                if application.state == 'adjust' and application.welfare_owner == self.env.user:
                    # Show Edit Button, Hide Add and Delete
                    application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>' \
                                        '<style>.fa-trash-o {display: none !important;}</style>' \
                                        '<style>.o_field_x2many_list_row_add {display: none !important;}</style>' \
                                        '<style>.o_btn_remove {display: none !important;}</style>'
                else:
                    # Hide Create and Edit Button
                    application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>' \
                                        '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                application.no_ce = False

    @api.model
    def create(self, vals):
        # print(self)
        # if len(self.depa_welfare_lines_ids) <= 0:
        #     raise ValidationError(_("กรุณาบันทึกรายการเบิกจ่ายก่อนบันทึกข้อมูล"))

        res = super(depa_welfare, self).create(vals)
        self.message_post(body="สร้างสวัสดิการเลือกอิสระแล้ว")
        return res

    @api.multi
    def write(self, vals):
        # if len(self.depa_welfare_lines_ids) <= 0:
        #     raise ValidationError(_("กรุณาบันทึกรายการเบิกจ่ายก่อนบันทึกข้อมูล"))

        res = super(depa_welfare, self).write(vals)
        # for line in self.depa_welfare_lines_ids:
        #     if len(line.receipt_attachment_ids) <= 0:
        #         raise ValidationError(_("กรุณาแนบไฟล์ใบเสร็จรับเงินหรือใบกำกับภาษี"))
        return res

    @api.multi
    def unlink(self):
        # print(self)
        for rec in self:
            if rec.state not in ["draft", "rejected", "completed"]:
                raise ValidationError(_("ไม่สามารถลบเอกสารที่เลือกได้เนื่องจากอยู่ในระหว่างดำเนินการ"))

        res = super(depa_welfare, self).unlink()
        return res

    @api.depends('welfare_fiscal_year')
    def _depends_welfare_year(self):
        for line in self:
            if line.welfare_fiscal_year:
                line.welfare_year = int(line.welfare_fiscal_year.fiscal_year)

    @api.depends('welfare_fiscal_year')
    def _depends_welfare_round(self):
        for line in self:
            if line.welfare_fiscal_year:
                welfare_round_line_obj = line.env['depa_welfare_round_lines'].search([
                    '|',
                    '&',
                    ('depa_welfare_round_lines_id.fiscal_year_id', '=', line.welfare_fiscal_year.id),
                    '&',
                    ('welfare_start', '<=', date.today()),
                    ('welfare_end', '>=', date.today()),
                    ('welfare_start', '>=', date.today()),
                ], limit=1)
                if welfare_round_line_obj:
                    line.welfare_round = welfare_round_line_obj.welfare_round
                    line.welfare_round_start = welfare_round_line_obj.welfare_start
                    line.welfare_round_end = welfare_round_line_obj.welfare_end

    @api.depends('depa_welfare_lines_ids.actual_amount', 'depa_welfare_lines_ids.actual_amount_hidden', 'depa_welfare_lines_ids.is_full_half')
    def _amount_total(self):
        for welfare in self:
            amount_sum = 0
            amount_sum_fund = 0
            fund = False
            for line in welfare.depa_welfare_lines_ids:
                amount_sum += line.actual_amount_hidden
                amount_sum_fund += line.actual_amount
                if line.is_full_half:
                    fund = line.is_full_half
            welfare.fund = fund
            welfare.amount_total = round(amount_sum, 2)
            welfare.amount_total_fund = round(amount_sum_fund, 2)


    @api.depends('depa_welfare_lines_ids.point_amount')
    def _point_total(self):
        for welfare in self:
            point_sum = 0
            for line in welfare.depa_welfare_lines_ids:
                point_sum += line.point_amount
            welfare.point_total = round(point_sum, 2)

    @api.depends('point_balance')
    def _depends_amount_balance(self):
        self.amount_balance = self.point_balance * 105

    @api.constrains('point_total')
    def _point_total_ctr(self):
        if round(self.point_total, 2) > self.point_balance:
            raise ValidationError(_("คะแนน คงเหลือไม่พอสำหรับทำรายการคะแนนที่ใช้ มากกว่า คะแนนคงเหลือ"))

    # @api.constrains('amount_total')
    # def _amount_total_ctr(self):
    #     if self.amount_total > self.amount_balance:
    #         raise ValidationError(_("จำนวนเงินคงเหลือไม่พอสำหรับทำรายการ จำนวนเงินที่ใช้ มากกว่า จำนวนเงินคงเหลือ"))

    def check_receipt_sorted(self):
        lines = self.depa_welfare_lines_ids
        for i, rec in enumerate(lines, 1):
            if i < len(lines):
                if lines[i-1].receipt_date > lines[i].receipt_date:
                    raise ValidationError(_("กรุณาเรียงลำดับค่าใช้จ่ายตามวันที่บนใบเสร็จก่อนและหลังตามลำดับ ก่อนส่งขออนุมัติ"))

    def check_welfare_inprogress(self):
        welfare_inprogress = self.env["depa_welfare"].search([
            ("welfare_owner", "=", self.env.uid),
            ("state", "not in", ["draft", "rejected", "completed"])
        ])
        if len(welfare_inprogress) >= 1 and self.state in ['draft']:
            raise ValidationError(_("ไม่สามารถส่งขออนุมัติได้เนื่องจากมีการเอกสารขออนุมัติเบิกสวัสดิการของคุณอยู่ในระหว่างดำเนินการ"))

    def check_welfare_basic_selected(self):
        basic = self.env["depa_welfare_basic"].search([
            ("welfare_basic_fiscal_year", "=", self._default_fiscal_year()),
            ("welfare_basic_owner", "=", self.env.uid),
            ("state", "in", ["completed"])
        ])
        if len(basic) == 0:
            raise ValidationError(
                _("ไม่สามารถทำรายการได้เนื่องจากคุณได้ยังไม่ได้ส่งแผนประกันของปีงบประมาณนี้"))

    def check_point_balance(self):
        if self.point_balance < self.point_total:
            raise ValidationError(
                _("คะแนนคงเหลือไม่พอสำหรับการส่งขออนุมัติรายการค่าใช้จ่ายสวัสดิการเลือกอิสระ"))

    def check_round_can_sent_welfare(self):
        if not (self.welfare_round_start <= date.today() <= self.welfare_round_end):
            raise ValidationError(_("ไม่สามารถส่งขออนุมัติได้เนื่องจากไม่ได้อยู่ในรอบการเบิกสวัสดิการ\nรอบในการเบิกต่อไปคือ "
                                    + str(self.welfare_round_start) + " ถึง " + str(self.welfare_round_end)))

    def check_item_more_one(self):
        more_one = False
        msg = "ในรายการค่าใช้จ่ายของคุณมีรายการที่ไม่สามารถสร้างได้มากกว่า 1 รายการ ได้แก่ \n"
        type_ids = []
        for line in self.depa_welfare_lines_ids:
            if not line.welfare_types_id.more_one_items:
                if line.welfare_types_id.id in type_ids:
                    more_one = True
                    msg += "- " + line.welfare_types_id.name + "\n"
                else:
                    type_ids.append(line.welfare_types_id.id)
        if more_one:
            raise ValidationError(_(msg))

    @api.multi
    def welfare_sent_to_inspector(self):
        # print(self)
        self.check_item_more_one()
        self.check_welfare_basic_selected()
        self.check_welfare_inprogress()
        self.check_point_balance()
        self.check_round_can_sent_welfare()

        if self._get_employee_info().is_in_probation:
            raise ValidationError(_("ไม่สามารถส่งขออนุมัติได้เนื่องจากอยู่ระหว่างทดลองงาน"))

        if len(self.depa_welfare_lines_ids) <= 0:
            raise ValidationError(_("กรุณาเพิ่มรายการเบิกจ่ายอย่างน้อย 1 รายการ"))

        if len(self.depa_welfare_lines_ids) > 1:
            self.check_receipt_sorted()

        if not self.fin_no:
            raise ValidationError(_("ไม่สามารถส่งขออนุมัติได้ เนื่องจาก FIN 100 ยังไม่เสร็จสิ้น"))

        if self.state == 'draft':
            seq = self.env['ir.sequence'].next_by_code('seq_depa_welfare')
            self.wel_no = "WEL" + str(self.welfare_year)[2:] + str(self.welfare_round) + str(seq.zfill(3))

        prevState = ""
        currentState = ""
        nextState = ""

        workflow_states = self._get_workflow_state()

        if self.state == 'draft':
            for i, workflow_state in enumerate(workflow_states):
                if workflow_state[0] == self.state:
                    prevState = workflow_states[i+1][0] # Adjust
                    currentState = workflow_states[i+2][0] # HR
                    nextState = workflow_states[i+3][0] # Approval
                    break
        elif self.state == 'adjust':
            for i, workflow_state in enumerate(workflow_states):
                if workflow_state[0] == self.state:
                    prevState = workflow_states[i][0] # Adjust
                    currentState = workflow_states[i+1][0] # HR
                    nextState = workflow_states[i+2][0] # Approval
                    break

        print(prevState +" | "+ currentState +" | "+ nextState)

        # Save to welfare history lines
        for rec in self.depa_welfare_lines_ids:
            welfare_lines_history = {
                "depa_welfare_lines_id": rec.id,
                "depa_welfare_lines_types_id": rec.welfare_types_id.id,
                "actual_amount_history": rec.actual_amount,
                "point_amount_history": rec.point_amount,
                "receipt_date_history": rec.receipt_date,
                "state_history": rec.current_state
            }
            self.env['depa_welfare_lines_history'].create(welfare_lines_history)

        # Get approval in this state
        approval = self.env['depa_welfare_approval_lines'].search([
            ('depa_welfare_approval_lines_id', '=', self.id),
            ('process_setting_id.state.code', '=', currentState)
        ], limit=1)

        print(approval.status)

        self.write({
            'prev_state': prevState,
            'state': currentState,
            'next_state': nextState,
            'state_approval': approval.process_approval.id
        })

        approval.write({
            'remark': '',
            'on_date': False,
            'status': 'pending'
        })

        self.message_post(body="สวัสดิการเลือกอิสระของคุณถูกส่งไปยังผู้ตรวจสอบเอกสารแล้ว")

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

        # return True

        # list = []
        #
        # if self.approver:
        #     for appr in self.approver:
        #         if appr.approve_active:
        #             if appr.approve_position:
        #                 astate = appr.approve_position
        #                 if astate not in list:
        #                     list.append(astate)
        #
        #     if "DirectorOfDepartment" in list:
        #         targetApprover = 'DirectorOfDepartment'
        #     elif "RelatedGroup" in list:
        #         targetApprover = 'RelatedGroup'
        #     elif "DirectorOfFinance" in list:
        #         targetApprover = 'DirectorOfFinance'
        #     elif "AssistantOfOffice" in list:
        #         targetApprover = 'AssistantOfOffice'
        #     elif "DeputyOfOffice" in list:
        #         targetApprover = 'DeputyOfOffice'
        #     elif "SmallNote" in list:
        #         targetApprover = 'SmallNote'
        #     elif "DirectorOfOffice" in list:
        #         targetApprover = 'DirectorOfOffice'



        # if self.fin_lines:
        #     for fl in self.fin_lines:
        #         fl.write({
        #             'fin100_state': 'sent'
        #         })

        # return True

    def action_make_approval_wizard(self):
        print(self)
        return {
            'name': "Make Approval Wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'depa_welfare_make_approval_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_welfare_id': self.id,
                'default_current_state': self.state,
                # 'default_employee_id': employee_id.id,
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }

            # raise ValidationError(_('Not your turn'))