# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError

STATES = [
    ('draft', 'ฉบับร่าง'),
    # ('adjust', 'ปรับแก้ไข'),
    # ('pending', 'รออนุมัติ (ผอ.ฝ่าย)'),
    ('completed', 'เสร็จสิ้น'),
    # ('rejected', 'ปฏิเสธ')
]
class kpi_setting_dsm_pm_models(models.Model):
    _name = 'kpi_setting_dsm_pm'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    fiscal_year = fields.Many2one(
        "fw_pfb_fin_system_fiscal_year",
        string="ปีงบประมาณ",
        required=True,
        copy=True,
        default=_default_fiscal_year
    )
    department_id = fields.Many2one(
        "hr.department"
    )
    department_name = fields.Char(
        string="ฝ่าย",
        compute="_depends_department_id",
        store=True
    )
    financial = fields.Float(
        string='Financial',
        readonly=True,
        digits=(10, 2),
    )
    customer = fields.Float(
        string='Customer',
        readonly=True,
        digits=(10, 2),
    )
    internal = fields.Float(
        string='Internal',
        readonly=True,
        digits=(10, 2),
    )
    learning = fields.Float(
        string='Learning',
        readonly=True,
        digits=(10, 2),
    )
    project_count_total = fields.Integer(
        string='ตัวชี้วัดรวม',
        readonly=True,
        compute='_sum_project_count_total',
    )
    project_weight_total = fields.Float(
        string='ค่าน้ำหนักรวม',
        readonly=True,
        compute='_sum_project_weight_total',
        digits=(10, 2),
    )
    project_budget_total = fields.Float(
        string='งบประมาณรวม',
        readonly=True,
        compute='_sum_project_budget_total',
        digits=(10, 2),
    )
    state = fields.Selection(
        STATES,
        string="สถานะ",
        default="draft"
    )
    kpi_setting_pm_lines_ids = fields.One2many(
        "kpi_setting_dsm_pm_lines",
        "kpi_setting_pm_lines_id",
        string="KPI",
        copy=True
    )
    kpi_setting_pm_approval_lines_ids = fields.One2many(
        "kpi_setting_pm_approval_lines",
        "kpi_setting_pm_approval_lines_id",
        string="ลำดับการอนุมัติ",
        copy=True
    )
    current_approval_id = fields.Many2one(
        'res.users'
    )
    approve_count = fields.Integer(
        default=0
    )

    @api.depends('kpi_setting_pm_lines_ids')
    def _sum_project_count_total(self):
        for line in self:
            line.project_count_total = len(line.kpi_setting_pm_lines_ids)

    @api.depends('kpi_setting_pm_lines_ids')
    def _sum_project_weight_total(self):
        for line in self:
            sum = 0
            for rec in line.kpi_setting_pm_lines_ids:
                sum += rec.project_weight
            line.kpi_project_total = sum

    @api.depends('kpi_setting_pm_lines_ids')
    def _sum_project_budget_total(self):
        sum = 0
        for line in self:
            for rec in line.kpi_setting_pm_lines_ids:
                sum += rec.project_budget
            line.project_budget_total = sum

    @api.depends('department_id')
    def _depends_department_id(self):
        for line in self:
            line.department_name = line.department_id.name

    def checkApproval(self):
        if len(self.kpi_setting_pm_approval_lines_ids) <= 0:
            raise ValidationError(_('กรุณาระบุผู้อนุมัติรายการ KPI ก่อนส่งอนุมัติ'))

        for line in self.kpi_setting_pm_approval_lines_ids:
            if line.employee_id.is_kpi_dummy:
                raise ValidationError(_('กรุณาผู้อนุมัติของคุณ ซึ่งจะต้องไม่ใช่ข้อมูล Dummy'))

    def checkLineStatus(self):
        if len(self.kpi_setting_pm_lines_ids) <= 0:
            raise ValidationError(_('กรุณาสร้างข้อมูล Master KPI ก่อนส่งอนุมัติ'))

        for line in self.kpi_setting_pm_lines_ids:
            if line.project_status == 'pending':
                raise ValidationError(_('คุณต้องอัพเดทข้อมูล KPI ให้เป็นข้อมูลที่ ดำเนินการแล้ว ทั้งหมด ก่อนส่งอนุมัติ'))

    def action_sent_kpi_to_approve(self):
        self.checkApproval()
        self.checkLineStatus()

        if self.state == 'draft' or self.state == 'adjust':
            self.kpi_setting_pm_approval_lines_ids[0].update({
                # 'approve_datetime': datetime.today(),
                'status': 'pending'
            })
            self.update({
                'current_approval_id': self.kpi_setting_pm_approval_lines_ids[0].employee_id.user_id.id,
                'state': 'pending',
            })
            self.approve_count = 1

    def action_kpi_dsm_pm_make_approval(self):
        return {
            'name': "Group Make Approval Wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'kpi_dsm_pm_make_approval_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_kpi_setting_dsm_pm_id': self.id,
                'default_current_state': self.state,
                # 'default_employee_id': employee_id.id,
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }

class kpi_setting_dsm_pm_lines_models(models.Model):
    _name = 'kpi_setting_dsm_pm_lines'

    kpi_setting_pm_lines_id = fields.Many2one(
        "kpi_setting_dsm_pm",
        required = True,
        ondelete='cascade'
    )
    kpi_setting_dsm_department_lines_id = fields.Many2one(
        "kpi_setting_dsm_department_lines"
    )
    # kpi_code = fields.Char(
    #     string="รหัสตัวชี้วัด"
    # )
    project_name = fields.Text(
        string="โครงการ"
    )
    project_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 2)
    )
    project_target = fields.Text(
        string="เป้าหมาย"
    )
    # kpi_target = fields.Text(string='เป้าหมาย')
    project_unit = fields.Many2one(
        'uom.uom',
        'หน่วย'
    )
    project_status = fields.Selection(
        [
            ("pending", "รอดำเนินการ"),
            ("done", "ดำเนินการแล้ว"),
        ],
        string="สถานะ",
        compute='_depends_is_done',
        default="pending",
        store=True
    )
    # kpi_definition = fields.Text(
    #     string="คำจำกัดความ"
    # )
    # kpi_calculate = fields.Selection(
    #     [
    #         ('sum', 'sum'),
    #         ('avg', 'average')
    #     ],
    #     string="คำนวณแบบ"
    # )
    project_budget = fields.Float(
        string="งบประมาณ",
        digits=(10, 2)
    )
    # kpi_has_assistant = fields.Boolean(
    #     string="มี ชสศด.",
    #     default=False
    # )
    # kpi_assistant_employee_id = fields.Many2one(
    #     "hr.employee",
    #     string="ระบุ ชสศด."
    # )
    # kpi_pm_definition_lines_ids = fields.Many2many(
    #     "kpi_pm_definition_lines",
    #     "kpi_setting_dsm_group_pm_definition_lines_rel",
    #     "kpi_setting_dsm_pm_lines_id",
    #     "kpi_pm_definition_lines_id",
    #     string='KPI Definition',
    # )
    # kpi_employee_lines_ids = fields.One2many(
    #     'kpi_employee_lines',
    #     'kpi_employee_lines_id',
    #     required=True,
    #     copy=True
    # )

    kpi_user_lines_ids = fields.One2many(
        'kpi_user_lines',
        'kpi_user_lines_id',
    )

    weight_total = fields.Float(
        string='น้ำหนักทั้งหมด',
        readonly=True,
        store=True,
        compute='_kpi_weight_total',
        digits=(10, 2),
    )
    is_done = fields.Boolean(
        string='ดำเนินงานแล้วเสร็จ'
    )
    is_validated = fields.Boolean(
        string='ตรวจผ่านแล้ว'
    )

    @api.depends('is_done')
    def _depends_is_done(self):
        for rec in self:
            if rec.is_done:
                rec.project_status = "done"
            else:
                rec.project_status = "pending"

    @api.depends('kpi_user_lines_ids')
    def _kpi_weight_total(self):
        for rec in self:
            sum = 0
            for line in rec.kpi_user_lines_ids:
                sum += line.kpi_user_weight
            rec.weight_total = sum
class kpi_master_user_lines_models(models.Model):
    _name = 'kpi_user_lines'

    kpi_user_lines_id = fields.Many2one(
        'kpi_setting_dsm_pm_lines',
        required=True,
        ondelete='cascade'
    )
    kpi_activity_id = fields.Text(
        string="งานที่ต้องทำ",
        required=True,
    )
    kpi_time = fields.Integer(
        string="ใช้เวลากี่วัน",
        required=True,
    )
    kpi_level = fields.Selection(
        [
            ('easy', 'ง่าย'),
            ('moderate', 'ปานกลาง'),
            ('hard', 'ยาก')
        ],
        string="ระดับความยากง่าย"
    )

    kpi_hr_user_id = fields.Many2one(
        "hr.employee",
        string="มอบหมาย",
    )
    kpi_user_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 2),
    )
    kpi_user_output = fields.Text(
        string="ผลลัพธ์"
    )

class kpi_setting_pm_approval_lines_models(models.Model):
    _name = 'kpi_setting_pm_approval_lines'

    kpi_setting_pm_approval_lines_id = fields.Many2one(
        'kpi_setting_dsm_pm',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string="ผู้อนุมัติ"
    )

    job_id = fields.Many2one(
        'hr.job',
        string="ตำแหน่ง",
        compute="_depends_employee_id",
        store=True
    )

    status = fields.Selection(
        [
            ("pending", "รออนุมัติ"),
            ("done", "อนุมัติแล้ว"),
            ("reject", "ปฏิเสธแล้ว"),
            ("adjust", "ปรับแก้ไข"),
        ],
        string="สถานะ"
    )

    approve_datetime = fields.Datetime(
        string="วัน/เวลา ที่อนุมัติ"
    )

    remark = fields.Text(
        string="หมายเหตุ"
    )

    @api.depends('employee_id')
    def _depends_employee_id(self):
        for rec in self:
            rec.job_id = rec.employee_id.job_id.id

# class kpi_master_employee_lines(models.Model):
#     _name = 'kpi_employee_lines'
#
#     kpi_employee_lines_id = fields.Many2one(
#         "kpi_setting_dsm_pm_lines",
#         required=True,
#     )
#     kpi_activity_id = fields.Text(
#         string="งานที่ต้องทำ",
#         required=True,
#     )
#
#     kpi_time = fields.Integer(
#         string="ใช้เวลากี่่วัน",
#         required=True,
#     )
#     kpi_level = fields.Selection(
#         [
#             ('easy', 'ง่าย'),
#             ('moderate', 'ปานกลาง')
#             ('hard', 'ยาก')
#         ],
#         string="ระดับความยากง่าย"
#     )
#
#     kpi_hr_user_id = fields.Many2one(
#         "hr.department",
#         string="PM (ส่วนงาน)",
#         domain="[('department_level', '=', 'DL1')]"
#     )
#     kpi_user_weight = fields.Float(
#         string="น้ำหนัก",
#         digits=(10, 2),
#     )
#     kpi_user_output = fields.Text(
#         string="ผลลัพธ์"
#     )


# class kpi_user_definition_lines(models.Model):
#     _name = 'kpi_user_definition_lines'
#
#     kpi_user_definition_lines_id = fields.Many2one(
#         "kpi_user_lines",
#         required=True,
#         ondelete='cascade'
#     )
#     kpi_user_def_level = fields.Integer(
#         string="ระดับ"
#     )
#     kpi_user_def_name = fields.Text(
#         string="คำจำกัดความ"
#     )
#     kpi_user_def_target = fields.Float(
#         string="เป้าหมาย",
#         digits=(10, 2)
#     )
#     kpi_user_def_unit = fields.Many2one(
#         'uom.uom',
#         'หน่วย'
#     )
