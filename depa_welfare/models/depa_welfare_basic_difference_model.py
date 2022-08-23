# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from itertools import groupby

FIN_100_READY_STATUS = 'completed'

FAMILY_RELATIONS = [
    ('children', 'บุตร'),
    ('parent', 'บิดา-มารดา'),
    ('spouse', 'คู่สมรส')
]

WELFARE_BACIC_STATE = [
    ('draft', 'ฉบับร่าง'),
    ('completed', 'เสร็จสมบูรณ์'),
    ('cancelled', 'ยกเลิก'),
]


class depa_welfare_basic_difference(models.Model):
    _name = 'depa_welfare_basic_difference'
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

    def _default_welfare_basic_year(self):
        basic_setting = self.env['depa_welfare_basic_setting'].search([
            ('start_date', '<=', date.today()),
            ('end_date', '>=', date.today()),
        ], limit=1)
        if basic_setting:
            return basic_setting.year.id

    def _get_my_point(self):
        employee_point = self.env['depa_welfare_hr_lines'].search([
            ('employee_id', '=', self._get_employee_info().id),
            ('hr_employee_id.year', '=', self._default_welfare_basic_year())
        ], limit=1)

        if employee_point:
            return employee_point.point

    def _get_life(self):
        life = self.env['life_insurance_lines'].search([
            ('life_insurance_lines_id.year', '=', self._default_welfare_basic_year())
        ])
        if life:
            return life.life_insurance_name

    def _get_age_round_up(self, dob):
        round_up = 0
        age = relativedelta(date.today(), dob)
        if age.months > 0 or age.days > 0:
            round_up = 1
        return age.years + round_up

    def _get_basic_welfare(self):
        basic = self.env['depa_welfare_basic'].search([
            ('employee_id', '=', self._get_employee_info().id),
            ('welfare_basic_fiscal_year', '=', self._default_welfare_basic_year()),
            ('state', '=', 'completed')
        ], limit=1)
        if not basic:
            raise ValidationError(_("ไม่พบรายการส่งแผนประกันประจำปีของคุณในปีนี้ \n สามารถสอบถามเพิ่มเติมได้ที่ ส่วนบริหารและพัฒนาบุคคล"))
        return basic


    basic_difference_no = fields.Char()
    basic_welfare_id = fields.Many2one(
        "depa_welfare_basic",
        default=_get_basic_welfare
    )

    welfare_fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_welfare_basic_year,
        # readonly=True,
    )

    plan_A = fields.Many2one(
        'life_insurance_lines',
        string="แผนA",
        default=lambda self: self._get_basic_welfare().plan_A.id
    )
    plan_B = fields.Many2one(
        'health_insurance_lines',
        string="แผนB",
        default=lambda self: self._get_basic_welfare().plan_B.id
    )
    sequence_A = fields.Integer(
        string="sequenceA",
        default=lambda self: self._get_basic_welfare().sequence_A
    )
    point_A = fields.Float(
        string="pointA",
        default=lambda self: self._get_basic_welfare().point_A
    )
    amount_A = fields.Float(
        string="จำนวนเงิน",
        default=lambda self: self._get_basic_welfare().amount_A
    )
    point_B = fields.Float(
        string="`pointB",
        default=lambda self: self._get_basic_welfare().point_B
    )
    amount_B = fields.Float(
        string="จำนวนเงิน",
        default=lambda self: self._get_basic_welfare().amount_B
    )
    welfare_basic_owner = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )
    employee_id = fields.Many2one(
        'hr.employee',
        default=lambda self: self._get_employee_info().id
    )
    emp_code = fields.Char(
        default=lambda self: self._get_employee_info().emp_code
    )
    emp_name = fields.Char(
        default=lambda self: self._get_employee_info().name
    )
    emp_dept_name = fields.Char(
        default=lambda self: self._get_employee_info().department_id.name
    )
    point_balance = fields.Float(
        default=_get_my_point
    )
    amount_balance = fields.Float(
        compute="_amount_balance_compute",
        store=True,
    )

    welfare_owner = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )
    point_basic_total = fields.Float(
        string="คะแนนรวม",
        compute="_point_basic_total",
        store=True,
        readonly=True,
        digits=(10, 2)
    )
    amount_basic_total = fields.Float(
        string="จำนวนเงินรวม",
        compute="_amount_basic_total",
        store=True,
        readonly=True
    )
    point_basic_remain = fields.Float(
        string="คะแนนคงเหลือ",
        compute="_point_basic_remain",
        store=True,
        readonly=True,
        digits=(10, 2)
    )
    amount_basic_remain = fields.Float(
        string="จำนวนเงินคงเหลือ",
        compute="_amount_basic_remain",
        store=True,
        readonly=True
    )
    welfare_year = fields.Char(
        compute='_depends_welfare_year',
        store=True,
    )

    welfare_basic_document_date = fields.Date(
        default=lambda self: date.today()
        # readonly=True,
    )
    welfare_basic_fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_welfare_basic_year,
        # readonly=True,
    )

    state = fields.Selection(
        WELFARE_BACIC_STATE,
        default='draft'
    )
    no_ce = fields.Html(
        string='no_create_edit',
        compute='_compute_no_ce_css',
        sanitize=False,
        store=False,
    )
    show_button_resend_to_inspector = fields.Boolean(
        'Show Resend Inspector',
        compute='_compute_show_button_resend_to_inspector',
        store=False
    )
    relative_ids = fields.One2many(
        'depa_welfare_basic_difference_lines',
        'user_relative_id',
        string='Employee',
        copy=True
    )
    confirm_timestamp = fields.Datetime(
        string='Confirm Timestamp',
    )
    cancel_timestamp = fields.Datetime(
        string='Cancel Timestamp',
    )
    basic_life_insurance_lines_ids = fields.One2many(
        'basic_life_insurance_lines',
        'basic_life_insurance_lines_id',
        # readonly=True,
        # copy=True
    )
    basic_health_insurance_lines_ids = fields.One2many(
        'basic_health_insurance_lines',
        'basic_health_insurance_lines_id',
        # readonly=True,
        # copy=True
    )
    life_lines_ids = fields.Many2many(
        'life_insurance_lines',
        'depa_welfare_basic_life_insurance_lines_rel',
        'depa_welfare_basic_id',
        'life_insurance_lines_id',
    )
    health_lines_ids = fields.Many2many(
        'health_insurance_lines',
        'depa_welfare_basic_health_insurance_lines_rel',
        'depa_welfare_basic_id',
        'health_insurance_lines_id',
    )
    attachment_lines_ids = fields.Many2many(
        'basic_welfare_attachment_lines',
        'depa_welfare_basic_attachment_lines_rel',
        'depa_welfare_basic_id',
        'basic_welfare_attachment_lines_id',
    )
    welfare_basic_start_date = fields.Date(
        string='วันที่เริ่ม'
    )
    welfare_basic_end_date = fields.Date(
        string='วันที่สิ้นสุด'
    )
    is_create = fields.Boolean(default=True)
    is_open_selection = fields.Boolean(default=False)
    show_sent_basic_button = fields.Boolean(default=True)

    @api.depends('point_balance')
    def _amount_balance_compute(self):
        for rec in self:
            rec.amount_balance = rec.point_balance * 105

    @api.depends('point_basic_total', 'point_balance')
    def _point_basic_remain(self):
        for rec in self:
            rec.point_basic_remain = rec.point_balance - rec.point_basic_total

    @api.depends('point_basic_remain')
    def _amount_basic_remain(self):
        for rec in self:
            rec.amount_basic_remain = rec.point_basic_remain * 105
    #
    #
    # @api.onchange('welfare_basic_fiscal_year')
    # def welfare_basic_fiscal_year_change(self):
    #     if not self.welfare_basic_fiscal_year or not self._default_welfare_basic_year():
    #         self.is_open_selection = False
    #         raise ValidationError(
    #             _("ไม่สามารถทำรายการได้เนื่องจากไม่ได้อยู่ในช่วงเวลาของการส่งแผนประกันประจำปี \n สามารถสอบถามเพิ่มเติมได้ที่ ส่วนบริหารและพัฒนาบุคคล"))
    #
    #     self.is_open_selection = True
    #     basic_setting = self.env['depa_welfare_basic_setting'].search([
    #         ('year', '=', self.welfare_basic_fiscal_year.id)
    #     ], limit=1)
    #     if basic_setting:
    #         self.welfare_basic_start_date = basic_setting.start_date
    #         self.welfare_basic_end_date = basic_setting.end_date
    #
    #
    # def check_welfare_basic_selected(self):
    #     basic = self.env["depa_welfare_basic"].search([
    #         ("welfare_basic_fiscal_year", "=", self._default_welfare_basic_year()),
    #         ("welfare_basic_owner", "=", self.env.uid),
    #         ("state", "in", ["completed"])
    #     ])
    #     if len(basic) >= 1 and self.state in ['draft']:
    #         raise ValidationError(
    #             _("ไม่สามารถทำรายการได้เนื่องจากคุณได้ส่งแผนประกันของปีงบประมานณนี้เรียบร้อยแล้ว"))
    #
    # def check_welfare_basic_due_date(self):
    #     basic = self.env["depa_welfare_basic_setting"].search([
    #         ("year", "=", self.welfare_basic_fiscal_year.id),
    #         ("start_date", "<=", date.today()),
    #         ("end_date", ">=", date.today())
    #     ], limit=1)
    #     if len(basic) < 1 and self.state in ['draft']:
    #         raise ValidationError(
    #             _("ไม่สามารถทำรายการได้เนื่องจากไม่ได้อยู่ในช่วงเวลาของการส่งแผนประกันประจำปี \n สามารถสอบถามเพิ่มเติมได้ที่ ส่วนบริหารและพัฒนาบุคคล"))

    # def check_welfare_basic_date_range(self):
    #     basic_setting = self.env["depa_welfare_basic_setting"].search([
    #         ("year", "=", self._default_welfare_basic_year()),
    #         ("start_date", "<=", date.today()),
    #         ("end_date", ">=", date.today())
    #     ])
    #     if len(basic_setting) < 1 and self.state in ['draft']:
    #         raise ValidationError(
    #             _("ไม่สามารถทำรายการได้เนื่องจากไม่ได้อยู่ในช่วงเวลาของการส่งแผนประกันประจำปี \n สามารถสอบถามเพิ่มเติมได้ที่ ส่วนบริหารและพัฒนาบุคคล"))

#     @api.model
#     def default_get(self, fields_list):
#         res = super(depa_welfare_basic_difference, self).default_get(fields_list)
#         relative_obj = self.env['hr.employee.relative'].search([
#             ('employee_id', '=', self._get_employee_info().id),
#         ])
#         values = []
#         for emp in relative_obj:
#             # print(emp.relation)
#             age = self._get_age_round_up(emp.date_of_birth)
#             if age > 0 and age <= 70:
#                 if emp.relation == 'CH':
#                     if age <= 25:
#                         values.append([
#                             0,
#                             0,
#                             {
#                                 'relative_title': emp.title_name.name,
#                                 'relative_name': emp.name,
#                                 'relation': emp.relation,
#                                 'age': emp.age,
#                                 'sequenceA': self.sequence_A,
#                                 'user_relative_id': self.id,
#                                 'date_of_birth': emp.date_of_birth,
#                                 'age_compute': self._get_age_round_up(emp.date_of_birth),
#                                 'welfare_basic_year': self._default_welfare_basic_year()
#                             }])
#                 elif emp.relation == 'SP':
#                     if age >= 15:
#                             values.append([
#                                 0,
#                                 0,
#                                 {
#                                     'relative_title': emp.title_name.name,
#                                     'relative_name': emp.name,
#                                     'relation': emp.relation,
#                                     'age': emp.age,
#                                     'sequenceA': self.sequence_A,
#                                     'user_relative_id': self.id,
#                                     'date_of_birth': emp.date_of_birth,
#                                     'age_compute': self._get_age_round_up(emp.date_of_birth),
#                                     'welfare_basic_year': self._default_welfare_basic_year()
#                                 }])
#                 else:
#                     values.append([
#                         0,
#                         0,
#                         {
#                             'relative_title': emp.title_name.name,
#                             'relative_name': emp.name,
#                             'relation': emp.relation,
#                             'age': emp.age,
#                             'sequenceA': self.sequence_A,
#                             'user_relative_id': self.id,
#                             'date_of_birth': emp.date_of_birth,
#                             'age_compute': self._get_age_round_up(emp.date_of_birth),
#                             'welfare_basic_year': self._default_welfare_basic_year()
#                         }])
#
#         basic_setting = self.env['depa_welfare_basic_setting'].search([
#             ('year', '=', self._default_welfare_basic_year()),
#         ], limit=1)
#         lifes = [(6, 0, basic_setting.life_insurance_lines_ids.ids)]
#         healths = [(6, 0, basic_setting.health_insurance_lines_ids.ids)]
#         attachments = [(6, 0, basic_setting.basic_welfare_attachment_lines_ids.ids)]
#         # life_values = []
#         # health_values = []
#         # attachment_values = []
#         # for life in basic_setting.life_insurance_lines_ids:
#         #
#         #     life_values.append([
#         #         0,
#         #         0,
#         #         {
#         #             'name': life.life_insurance_name,
#         #             'point': life.life_insurance_point,
#         #             'basic_life_insurance_desc_lines_ids': [
#         #                 (
#         #                     0,
#         #                     0,
#         #                     {
#         #                         'life_insurance_desc': desc.life_insurance_desc,
#         #                         'life_insurance_package': desc.life_insurance_package
#         #                     }
#         #                 )  for desc in life.life_insurance_desc_lines_ids
#         #             ]
#         #         }
#         #     ])
#         # for health in basic_setting.health_insurance_lines_ids:
#         #     health_values.append([
#         #         0,
#         #         0,
#         #         {
#         #             'name': health.health_insurance_name,
#         #             'point': health.health_insurance_point,
#         #             'basic_health_insurance_desc_lines_ids': [
#         #                 (
#         #                     0,
#         #                     0,
#         #                     {
#         #                         'health_insurance_desc': desc.health_insurance_desc,
#         #                         'health_insurance_package': desc.health_insurance_package
#         #                     }
#         #                 )  for desc in health.health_insurance_desc_lines_ids
#         #             ]
#         #         }
#         #     ])
#         # for attach in basic_setting.basic_welfare_attachment_lines_ids:
#         #     attachment_values.append([
#         #         0,
#         #         0,
#         #         {
#         #             'name': attach.name,
#         #             'basic_attachment_ids': [
#         #                 (
#         #                     6,
#         #                     0,
#         #                     attach.basic_attachment_ids.ids
#         #                 )
#         #             ]
#         #         }
#         #     ])
#         res.update({
#             'relative_ids': values,
#             'life_lines_ids': lifes,
#             'health_lines_ids': healths,
#             'attachment_lines_ids': attachments,
#             'show_sent_basic_button': basic_setting.show_sent_basic_button
#             # 'basic_life_insurance_lines_ids': life_values,
#             # 'basic_health_insurance_lines_ids': health_values,
#             # 'basic_attachment_lines_ids': attachment_values,
#
#         })
#         return res
#
#     @api.multi
#     def name_get(self):
#         return [(rec.id, rec.wel_basic_no) for i, rec in enumerate(self)]
#
#     @api.onchange('plan_A')
#     def onchange_planA(self):
#         point = self.env['life_insurance_lines'].search([
#             ('id', '=', self.plan_A.id),
#         ])
#         self.point_A = point.life_insurance_point
#         self.amount_A = point.life_insurance_point * 105
#         self.sequence_A = point.sequence
#         if len(self.relative_ids) > 0:
#             for rel in self.relative_ids:
#                 rel.planA = None
#                 rel.PointA = 0
#
#
#     @api.onchange('plan_B')
#     def onchange_planB(self):
#         point = self.env['health_insurance_lines'].search([
#             ('id', '=', self.plan_B.id),
#         ])
#         self.point_B = point.health_insurance_point
#         self.amount_B = point.health_insurance_point * 105
#
#     # @api.onchange('is_create')
#     # def _onchange_is_create(self):
#         # print(self.is_create)
#         # if self.is_create:
#             # relative_obj = self.env['hr.employee.relative'].search([
#             #     ('employee_id', '=', self._get_employee_info().id),
#             # ])
#             # values = []
#             # for emp in relative_obj:
#             #     # print(emp.relation)
#             #     age = self._get_age_round_up(emp.date_of_birth)
#             #     if age > 0 and age <= 70:
#             #         if emp.relation == 'CH':
#             #             if age <= 25 :
#             #                 values.append([0, 0, {
#             #                     'relative_name': emp.name,
#             #                     'relation': emp.relation,
#             #                     'age': emp.age,
#             #                     'user_relative_id': self.id,
#             #                     'date_of_birth': emp.date_of_birth
#             #                 }])
#             #         elif emp.relation == 'SP':
#             #             if age >= 15:
#             #                 values.append([0, 0, {
#             #                     'relative_name': emp.name,
#             #                     'relation': emp.relation,
#             #                     'age': emp.age,
#             #                     'user_relative_id': self.id,
#             #                     'date_of_birth': emp.date_of_birth
#             #                 }])
#             #         else:
#             #             values.append([0, 0, {
#             #                 'relative_name': emp.name,
#             #                 'relation': emp.relation,
#             #                 'age': emp.age,
#             #                 'user_relative_id': self.id,
#             #                 'date_of_birth': emp.date_of_birth
#             #             }])
#             #
#             # self.update({
#             #     'relative_ids': values,
#             # })
#
#             # basic = self.env['depa_welfare_basic_setting'].search([
#             #     ('year', '=', self._default_fiscal_year()),
#             # ])
#             # life_obj = self.env['life_insurance_lines'].search([
#             #     ('life_insurance_lines_id', '=', basic.id),
#             # ])
#             # life_values = []
#             # for life in life_obj:
#             #     #print(life.life_insurance_name)
#             #     life_values.append([0, 0, {
#             #         'life_insurance_name': life.life_insurance_name,
#             #         'life_insurance_point': life.life_insurance_point,
#             #         'life_insurance_desc_lines_ids' : self.env['life_insurance_desc_lines'].search([('life_insurance_desc_lines_id', '=', life.id),])
#             #
#             #     }])
#             # self.update({
#             #     'life_insurance_lines_ids': life_values,
#             # })
#             #
#             # health_obj = self.env['health_insurance_lines'].search([
#             #     ('health_insurance_lines_id', '=', basic.id),
#             # ])
#             # health_values = []
#             # for health in health_obj:
#             #     # print(life.life_insurance_name)
#             #     health_values.append([0, 0, {
#             #         'health_insurance_name': health.health_insurance_name,
#             #         'health_insurance_point': health.health_insurance_point,
#             #         'health_insurance_desc_lines_ids': self.env['health_insurance_desc_lines'].search([('health_insurance_desc_lines_id', '=', health.id), ])
#             #
#             #     }])
#             # self.update({
#             #     'health_insurance_lines_ids': health_values,
#             # })
#
#
#     @api.depends('welfare_fiscal_year')
#     def _get_fin_no(self):
#         # print(self)
#         for rec in self:
#             fin_100 = self.env['fw_pfb_fin_system_100'].search([
#                 ('is_welfare', '=', True),
#                 ('fiscal_year.fiscal_year', '=', rec.welfare_year),
#                 ('state', '=', FIN_100_READY_STATUS),
#             ], limit=1)
#             if fin_100:
#                 rec.fin_no = fin_100.id
#             else:
#                 rec.fin_no = False
#
    @api.depends('relative_ids.PointA', 'relative_ids.PointB', 'point_A', 'point_B')
    def _point_basic_total(self):
        for point in self:
            point_sum = 0
            for line in point.relative_ids:
                point_sum += line.PointA + line.PointB

        self.point_basic_total = point_sum

    @api.depends('relative_ids.amountA', 'relative_ids.amountB', 'amount_A', 'amount_B')
    def _amount_basic_total(self):
        for amount in self:
            amount_sum = 0
            for line in amount.relative_ids:
                amount_sum += line.amountA + line.amountB

            amount.amount_basic_total = amount_sum

    @api.constrains('point_basic_remain')
    def _point_total_ctr(self):
        if self.point_basic_remain >= 0:
            raise ValidationError(_("คะแนน (ส่วนต่าง) ไม่เข้าเงื่อนไขในการใช้สิทธิหักเงินส่วนต่างได้ \n กรุณาติดต่อสอบถามเพิ่มเติมได้ที่ ส่วนบริหารและพัฒนาบุคคล"))
#
#     @api.constrains('point_basic_total')
#     def _point_total_ctr(self):
#         if self.point_basic_total > self.point_balance:
#             raise ValidationError(_("จำนวน Point คงเหลือไม่พอสำหรับทำรายการ"))
#
#     # @api.depends('state')
#     # def _get_current_user(self):
#     #     for rec in self:
#     #         rec.current_user = self.env.user
#
#     @api.depends('state')
#     def _compute_no_ce_css(self):
#         for application in self:
#             # Modify below condition
#             if application.state != 'draft':
#                 # Hide Create and Edit Button
#                 application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>' \
#                                     '<style>.o_form_button_edit {display: none !important;}</style>'
#                 # Show Edit Button, Hide Add and Delete
#                 # application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>' \
#                 #                     '<style>.fa-trash-o {display: none !important;}</style>' \
#                 #                     '<style>.o_field_x2many_list_row_add {display: none !important;}</style>' \
#                 #                     '<style>.o_btn_remove {display: none !important;}</style>'
#
#             else:
#                 application.no_ce = '<style>.o-kanban-button-new {display: none !important;}</style>'
#
#
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(depa_welfare_basic, self).fields_view_get(
#                     view_id=view_id,
#                     view_type=view_type,
#                     toolbar=toolbar,
#                     submenu=submenu
#         )
#
#         if view_type == 'form':
#             # print(self.env.user.id)
#             current_usr = self.env.user.id
#             welfares = self.env['depa_welfare_basic'].search([
#                 ('state', '=', 'draft'),
#                 ('create_uid', '=', current_usr)
#             ])
#             basic_setting = self.env['depa_welfare_basic_setting'].search([
#                 ('year', '=', self._default_welfare_basic_year()),
#             ], limit=1)
#
#             for welfare in welfares:
#                 # welfare.fin_no = 'TestingFin100NO.X'
#                 fin_100 = self.env['fw_pfb_fin_system_100'].search([
#                     ('is_welfare', '=', True),
#                     ('fiscal_year.fiscal_year', '=', welfare.welfare_year),
#                     ('state', '=', FIN_100_READY_STATUS),
#                 ], limit=1)
#                 if fin_100:
#                     welfare.fin_no = fin_100.id
#                 else:
#                     welfare.fin_no = False
#
#                 welfare.point_balance = self._get_my_point()
#                 welfare.show_sent_basic_button = basic_setting.show_sent_basic_button
#
#         return res
#
#
#
#     @api.depends('welfare_fiscal_year')
#     def _depends_welfare_year(self):
#         for line in self:
#             if line.welfare_fiscal_year:
#                 line.welfare_year = int(line.welfare_fiscal_year.fiscal_year)
    @api.multi
    def sent_welfare_basic_difference(self):

        if self.state == 'draft':
            seq = self.env['ir.sequence'].next_by_code('seq_depa_basic_welfare_difference')
            code_no = "BDWEL" + str(self.welfare_basic_fiscal_year.fiscal_year)[2:] + '-' + str(seq.zfill(3))

            self.update({
                'basic_difference_no': code_no,
                'state': 'completed'
            })
            self.confirm_timestamp = datetime.now()

            # Update point
            employee_point = self.env['depa_welfare_hr_lines'].search([
                ('employee_id', '=', self.employee_id.id),
                ('hr_employee_id.year', '=', self.welfare_basic_fiscal_year.id)
            ], limit=1)

            if employee_point:
                point_remain = round(employee_point.point, 2) - self.point_basic_total
                if point_remain < 0:
                    point_remain = 0

                employee_point.write({
                    "point": point_remain,
                    "is_sent_point_update": True
                })
                # Save to point history lines
                point_history = {
                    "desc": "เลือกแผนประกันสุขภาพ (หักเงินส่วนต่าง)",
                    "on_date": datetime.now(),
                    "point_type": 'minus',
                    "point_usage": self.point_basic_total,
                    "point_balance": point_remain,
                    "wel_doc_no": self.basic_difference_no,
                    "employee_id": self.employee_id.id,
                    "welfare_fiscal_year": self.welfare_basic_fiscal_year.id
                }
                self.env['point_history_lines'].create(point_history)

        self.message_post(body="เลือกแผนประกัน (หักเงินส่วนต่าง) เรียบร้อยแล้ว")

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

#     @api.multi
#     def sent_welfare_basic(self):
#
#         self.check_welfare_basic_selected()
#         self.check_welfare_basic_due_date()
#         # if not self.is_open_selection:
#         #     raise ValidationError(
#         #         _("ไม่สามารถทำรายการได้เนื่องจากไม่ได้อยู่ในช่วงเวลาของการส่งแผนประกันประจำปี \n สามารถสอบถามเพิ่มเติมได้ที่ ส่วนบริหารและพัฒนาบุคคล"))
#
#
#         if self.state == 'draft':
#             seq = self.env['ir.sequence'].next_by_code('seq_depa_basic_welfare')
#             code_no = "BWEL" + str(self.welfare_year)[2:] + '-' + str(seq.zfill(3))
#
#             self.update({
#                 'wel_basic_no': code_no,
#                 'state': 'completed'
#             })
#             self.confirm_timestamp = datetime.now()
#
#             # Update point
#             employee_point = self.env['depa_welfare_hr_lines'].search([
#                 ('employee_id', '=', self.employee_id.id),
#                 ('hr_employee_id.year', '=', self.welfare_basic_fiscal_year.id)
#             ], limit=1)
#
#             if employee_point:
#                 point_remain = employee_point.point - self.point_basic_total
#                 employee_point.write({
#                     "point": point_remain,
#                     "is_sent_point_update": True
#                 })
#                 print(self.wel_basic_no)
#                 # Save to point history lines
#                 point_history = {
#                     "desc": "เลือกแผนประกันสุขภาพ",
#                     "on_date": datetime.now(),
#                     "point_type": 'minus',
#                     "point_usage": self.point_basic_total,
#                     "point_balance": point_remain,
#                     "wel_doc_no": self.wel_basic_no,
#                     "employee_id": self.employee_id.id,
#                     "welfare_fiscal_year": self.welfare_basic_fiscal_year.id
#                 }
#                 self.env['point_history_lines'].create(point_history)
#
#         self.message_post(body="เลือกแผนประกันเรียบร้อยแล้ว")
#
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'reload',
#         }
#
#     @api.multi
#     def action_to_cancel(self):
#         if self.state == 'completed':
#             self.update({
#                 'state': 'cancelled'
#             })
#             self.cancel_timestamp = datetime.now()
#
#             # Update point
#             employee_point = self.env['depa_welfare_hr_lines'].search([
#                 ('employee_id', '=', self.employee_id.id),
#                 ('hr_employee_id.year', '=', self.welfare_basic_fiscal_year.id)
#             ], limit=1)
#
#             if employee_point:
#                 point_remain = employee_point.point + self.point_basic_total
#                 employee_point.write({
#                     "point": point_remain,
#                     "is_sent_point_update": True
#                 })
#
#                 # Save to point history lines
#                 point_history = {
#                     "desc": "คืนคะแนนกลับให้ผู้ใช้เนื่องจากเอกสารถูกยกเลิก",
#                     "on_date": datetime.now(),
#                     "point_type": 'add',
#                     "point_usage": self.point_basic_total,
#                     "point_balance": point_remain,
#                     "wel_doc_no": self.wel_basic_no,
#                     "employee_id": self.employee_id.id,
#                     "welfare_fiscal_year": self.welfare_basic_fiscal_year.id
#                 }
#                 self.env['point_history_lines'].create(point_history)
#
#         self.message_post(body="เอกสารถูกยกเลิก")
#
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'reload',
#         }
#
#     @api.multi
#     def unlink(self):
#         for rec in self:
#             if rec.state not in ["draft"]:
#                 raise ValidationError(_("ไม่สามารถลบเอกสารที่ถูกดำเนินการแล้วได้"))
#
#         res = super(depa_welfare_basic, self).unlink()
#         return res
#
#
#     @api.depends('state')
#     def _compute_show_button_resend_to_inspector(self):
#         for rec in self:
#             if rec.state == 'adjust' and self.env.user == rec.welfare_owner:
#                 rec.show_button_resend_to_inspector = True
#             else:
#                 rec.show_button_resend_to_inspector = False
#
#
#

class depa_welfare_basic_difference_lines(models.Model):
    _name = 'depa_welfare_basic_difference_lines'

    def list_diff(self, li1, li2):
        return list(set(li1) - set(li2)) + list(set(li2) - set(li1))

    def _get_employee_info(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ])
        return employee

    def _default_welfare_basic_year(self):
        basic_setting = self.env['depa_welfare_basic_setting'].search([
            ('start_date', '<=', date.today()),
            ('end_date', '>=', date.today()),
        ], limit=1)
        if basic_setting:
            return basic_setting.year.id

    def _get_basic_welfare(self):
        basic = self.env['depa_welfare_basic'].search([
            ('employee_id', '=', self._get_employee_info().id),
            ('welfare_basic_fiscal_year', '=', self._default_welfare_basic_year()),
            ('state', '=', 'completed')
        ], limit=1)
        if basic:
            return basic.id

    def _get_relative_available(self):
        my_relative_ids = []
        relative_ids = []
        my_relatives = self.env['hr.employee.relative'].search([
            ('employee_id', '=', self._get_employee_info().id)
        ])
        if my_relatives:
            for rel in my_relatives:
                if rel.age_round_up > 0 and rel.age_round_up <= 70:
                    if rel.relation == 'CH':
                        if rel.age_round_up <= 25:
                            my_relative_ids.append(rel.id)
                    elif rel.relation == 'SP':
                        if rel.age_round_up >= 15:
                            my_relative_ids.append(rel.id)
                    else:
                        my_relative_ids.append(rel.id)

        basic = self.env['depa_welfare_basic'].browse(self._get_basic_welfare())
        if basic.relative_ids:
            for relative in basic.relative_ids:
                if relative.relative_id:
                    relative_ids.append(relative.relative_id.id)

        relative_can_select_ids = self.list_diff(my_relative_ids, relative_ids)
        domain = [
            ('employee_id', '=', self._get_employee_info().id),
            ('id', 'in', relative_can_select_ids)
        ]

        # print(relative_can_select_ids)
        # if len(relative_can_select_ids) > 0:
        #     domain.append(('id', 'in', relative_can_select_ids))


        return domain

    def _get_age_round_up(self, dob):
        round_up = 0
        age = relativedelta(date.today(), dob)
        if age.months > 0 or age.days > 0:
            round_up = 1
        return age.years + round_up

    relative_id = fields.Many2one(
        "hr.employee.relative",
        string="ชื่อ-นามสกุล",
        domain=_get_relative_available,
    )
    relative_title = fields.Char(
        string="คำนำหน้า"
    )
    relative_name = fields.Char(
        string="ชื่อ-นามสกุล"
    )
    relation = fields.Selection(
        string="ความสัมพันธ์",
        selection=[
            ('MO', 'มารดา'),
            ('FA', 'บิดา'),
            ('SP', 'คู่สมรส'),
            ('CH', 'บุตร'),
        ],
    )
    age = fields.Char(
        string="อายุ"
    )
    date_of_birth = fields.Date(
        string='Date of Birth',
    )
    age_compute = fields.Float(
        string='Age Compute'
    )
    planA = fields.Many2one(
        'life_insurance_lines',
        string="แผนA"
    )
    PointA = fields.Float(
        string="Point",
        digits=(10, 2)
    )
    amountA = fields.Float(
        string="จำนวนเงิน"
    )
    planB = fields.Many2one(
        'health_insurance_lines',
        string="แผนB"
    )
    PointB = fields.Float(
        string="Point",
        digits=(10, 2)
    )
    amountB = fields.Float(
        string="จำนวนเงิน"
    )
    welfare_basic_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year'
    )
    sequenceA = fields.Integer(
        string="ลำดับ",
        compute='_sequences_compute',
    )
    PointTotal = fields.Float(
        string="คะแนนรวม",
        compute="_point_total",
        digits=(10, 2)
    )
    AmountTotal = fields.Float(
        string="จำนวนเงินรวม",
        compute="_amount_total",
    )

    user_relative_id = fields.Many2one(
        'depa_welfare_basic_difference',
        string="basic welfare id",
        ondelete='cascade'
    )
    row_no = fields.Integer()
    row_nos = fields.Integer(
        compute="_compute_row_no",
    )

    @api.onchange('planA')
    def onchange_planA(self):
        point = self.env['life_insurance_lines'].search([
            ('id', '=', self.planA.id),
        ])
        self.PointA = point.life_insurance_point
        self.amountA = point.life_insurance_point * 105


    @api.onchange('planB')
    def onchange_planB(self):
        point = self.env['health_insurance_lines'].search([
            ('id', '=', self.planB.id),
        ])
        self.PointB = point.health_insurance_point
        self.amountB = point.health_insurance_point * 105

    @api.depends('user_relative_id.relative_ids')
    def _compute_row_no(self):
        for line in self:
            for i, rec in enumerate(line.user_relative_id.relative_ids, 1):
                rec.row_nos = i
                if rec.user_relative_id.point_balance > 0:  # remain point more 0
                    if rec.relation:
                        if rec.row_nos > 1 and rec.relation != 'CH':
                            rec.relative_id = False
                            rec.planA = False
                            rec.planB = False
                            raise ValidationError(_("รายชื่อญาติที่เลือกในลำดับที่ 2 ขึ้นไปต้องเป็น บุตร เท่านั้น"))
                else:
                    if rec.relation:
                        if rec.relation != 'CH':
                            rec.relative_id = False
                            rec.planA = False
                            rec.planB = False
                            raise ValidationError(_("รายชื่อญาติที่เลือกต้องเป็น บุตร เท่านั้น"))

    @api.depends('PointA', 'PointB')
    def _point_total(self):
        for rec in self:
            rec.PointTotal = rec.PointB + rec.PointA

    @api.depends('amountA', 'amountB')
    def _amount_total(self):
        for rec in self:
            rec.AmountTotal = rec.amountA + rec.amountB

    @api.depends('user_relative_id.sequence_A')
    def _sequences_compute(self):
        for rec in self:
            rec.sequenceA = rec.user_relative_id.sequence_A

    @api.constrains('planA', 'planB')
    def _plan_lines_ctr(self):
        for line in self:
            if not line.planA or not line.planB:
                raise ValidationError(_("กรุณาเลือกแผนสำหรับครอบครัวให้ครบถ้วนก่อนทำการบันทึกข้อมูล"))

    @api.onchange('relative_id')
    def onchange_relative_id(self):
        if not self.relative_id: #on create add a line
            self.row_no = len(self.user_relative_id.relative_ids)

        self.relative_title = self.relative_id.title_name.name
        self.relation = self.relative_id.relation
        self.age = self.relative_id.age
        self.date_of_birth = self.relative_id.date_of_birth
        self.age_compute = self._get_age_round_up(self.relative_id.date_of_birth)

        if self.user_relative_id.relative_ids:
            ids = []
            for relative in self.user_relative_id.relative_ids:
                if relative.relative_id.id:
                    ids.append(int(relative.relative_id.id))
            if ids:
                for key, group in groupby(sorted(ids)):
                    if len(list(group)) >= 3:
                        raise ValidationError(_("ไม่สามารถเลือกรายชื่อญาติซ้ำกันได้"))

        # if self.user_relative_id.point_balance > 0: #remain point more 0
        #     if self.relation:
        #         if self.row_no > 1 and self.relation != 'CH':
        #             raise ValidationError(_("รายชื่อญาติที่เลือกในลำดับที่ 2 ขึ้นไปต้องเป็น บุตร เท่านั้น"))
        # else:
        #     if self.relation:
        #         if self.relation != 'CH':
        #             raise ValidationError(_("รายชื่อญาติที่เลือกต้องเป็น บุตร เท่านั้น"))


        # print(self.relative_id)
        # print(len(self.user_relative_id.relative_ids))
        # print(self.user_relative_id.point_balance)







# class basic_life_insurance_lines(models.Model):
#     _name = 'basic_life_insurance_lines'
#
#     name = fields.Char(
#         string="แผนประกันชีวิต"
#     )
#     point = fields.Float(
#         string="คะแนนที่ใช้"
#     )
#     basic_life_insurance_lines_id = fields.Many2one(
#         'depa_welfare_basic',
#         ondelete = 'cascade'
#     )
#     basic_life_insurance_desc_lines_ids = fields.One2many(
#         "basic_life_insurance_desc_lines",
#         "basic_life_insurance_desc_id",
#         # readonly=True,
#         # copy=True
#     )
#
# class basic_life_insurance_desc_lines(models.Model):
#     _name = 'basic_life_insurance_desc_lines'
#
#     life_insurance_desc = fields.Text(
#         string='รายละเอียด'
#     )
#     life_insurance_package = fields.Float(
#         string='ความคุ้มครอง'
#     )
#     basic_life_insurance_desc_id = fields.Many2one(
#         'basic_life_insurance_lines',
#         ondelete='cascade'
#     )
#
# class basic_health_insurance_lines(models.Model):
#     _name = 'basic_health_insurance_lines'
#
#     name = fields.Char(
#         string="แผนประกันสุขภาพ"
#     )
#     point = fields.Float(
#         string="คะแนนที่ใช้"
#     )
#     basic_health_insurance_lines_id = fields.Many2one(
#         'depa_welfare_basic',
#         ondelete='cascade'
#     )
#     basic_health_insurance_desc_lines_ids = fields.One2many(
#         "basic_health_insurance_desc_lines",
#         "basic_health_insurance_desc_id",
#         # readonly=True,
#         # copy=True
#     )
#
# class basic_health_insurance_desc_lines(models.Model):
#     _name = 'basic_health_insurance_desc_lines'
#
#     health_insurance_desc = fields.Text(
#         string='รายละเอียด'
#     )
#     health_insurance_package = fields.Float(
#         string='ความคุ้มครอง'
#     )
#     basic_health_insurance_desc_id = fields.Many2one(
#         'basic_health_insurance_lines',
#         ondelete='cascade'
#     )






