# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError

STATES = [
    ('draft', 'ฉบับร่าง'),
    ('adjust', 'ปรับแก้ไข'),
    ('pending', 'รออนุมัติ (ผอ.ฝ่ายกลยุทธ์ฯ)'),
    ('completed', 'เสร็จสิ้น'),
    ('rejected', 'ปฏิเสธ')
]
class kpi_setting_dsm_models(models.Model):
    _name = 'kpi_setting_dsm'

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
    # DE = fields.Float(
    #     string='กลุ่มงานเศรษฐกิจดิจิทัล',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    # SM = fields.Float(
    #     string='กลุ่มงานสังคมและกำลังคนดิจิทัล',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    # DI = fields.Float(
    #     string='กลุ่มงานโครงการพิเศษ',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    # VP = fields.Float(
    #     string='กลุ่มงานยุทธศาสตร์และบริหาร',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    # EP = fields.Float(
    #     string='กลุ่มงานบริหารสำนักงาน',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    # DB = fields.Float(
    #     string='กลุ่มงานกิจการสาขา',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    # GBDi = fields.Float(
    #     string='GBDi',
    #     readonly=True,
    #     compute='_sum_group_total',
    #     digits=(10, 2),
    # )
    group_weight = fields.Float(
        string='ค่าน้ำหนักกลุ่มงานรวม',
        readonly=True,
        compute='_sum_group_total',
        digits=(10, 2),
    )
    kpi_weight_total = fields.Float(
        string='ค่าน้ำหนักรวม',
        readonly=True,
        compute='_sum_kpi_weight_total',
        digits=(10, 2),
    )
    kpi_setting_dsm_lines_ids = fields.One2many(
        "kpi_setting_dsm_lines",
        "kpi_setting_dsm_lines_id",
        string="KPI",
        copy=True
    )
    kpi_setting_dsm_approval_lines_ids = fields.One2many(
        "kpi_setting_dsm_approval_lines",
        "kpi_setting_dsm_approval_lines_id",
        string="ลำดับการอนุมัติ",
        copy=True
    )
    state = fields.Selection(
        STATES,
        string="สถานะ",
        default="draft"
    )
    current_approval_id = fields.Many2one(
        'res.users'
    )
    approve_count = fields.Integer(
        default=0
    )
    department_ids = fields.One2many(
        'kpi_sum_department_lines',
        'dept_id',
        string='Department',

    )

    @api.onchange('fiscal_year')
    def _onchange_years(self):
        year = self.fiscal_year.id
        kpi_master = self.env['kpi_master'].search([
            ('fiscal_year', '=', year),
        ])
        kpi_master_lines = self.env['kpi_master_lines'].search([
            ('kpi_master_lines_id', '=', kpi_master.id),
        ])


        kpi_lines = []
        approval_ids = []
        group_id = self.env['res.groups'].search([('name', 'like', 'สามารถอนุมัติ KPI ระบบส่วนติดตามฯ')], limit=1)
        if group_id:
            if group_id.users:
                for user in group_id.users:
                    approval_ids.append(user.id)

        if kpi_master_lines:
            fin = 0.0
            cus = 0.0
            inter = 0.0
            learn = 0.0
            for rec in kpi_master_lines:
                # kpi_def = self.env['kpi_definition_lines'].search([
                #     ('kpi_definition_lines_id', '=', rec.id),
                # ])
                if rec.kpi_master_bsc == 'F':
                    fin += rec.kpi_master_weight
                    self.financial = fin
                elif rec.kpi_master_bsc == 'C':
                    cus += rec.kpi_master_weight
                    self.customer = cus
                elif rec.kpi_master_bsc == 'I':
                    inter += rec.kpi_master_weight
                    self.internal = inter
                else:
                    learn += rec.kpi_master_weight
                    self.learning = learn

                kpi_setting_dsm_lines = self.env['kpi_setting_dsm_lines'].search([
                    ('kpi_master_lines_id', '=', rec.id),
                ])
                
                if(kpi_setting_dsm_lines.is_done != True):
                    #print(kpi_setting_dsm_lines.is_done)
                    # def_lines = []
                    # for line in rec.kpi_definition_lines_ids:
                    #
                    #     def_lines.append(
                    #         (
                    #             0,
                    #             0,
                    #             {
                    #                 'kpi_group_def_level': line.kpi_definition_level,
                    #                 'kpi_group_def_name': line.kpi_definition_name,
                    #             }
                    #         )
                    #     )


                    kpi_lines.append(
                        (
                            0,
                            0,
                            {
                                # 'kpi_setting_dsm_lines_id': rec.id,
                                'kpi_master_lines_id': rec.id,
                                'kpi_code': rec.kpi_master_code,
                                'kpi_name': rec.kpi_master_name,
                                'kpi_weight': rec.kpi_master_weight,
                                'kpi_target': [(6, 0, rec.kpi_target_lines_ids.ids)],
                                # 'kpi_unit': rec.kpi_master_unit.id,
                                'kpi_bsc': rec.kpi_master_bsc,
                                'kpi_budget': rec.kpi_budget_amount,
                                'kpi_calculate': 'sum',
                                'kpi_master_definition_lines_ids': [(6, 0, rec.kpi_definition_lines_ids.ids)],
                                'kpi_master_target_lines_ids': [(6, 0, rec.kpi_target_lines_ids.ids)],
                                'kpi_status': 'pending',
                                'is_done': False
                                # 'kpi_group_definition_line_ids': def_lines,
                            }
                        )
                    )
        # self.update({'kpi_setting_dsm_lines_ids': [(5,)]})
        # print(kpi_lines)
        employee_dummy = self.env['hr.employee'].search([
            ('user_id', 'in', approval_ids)
        ],limit=1)
        self.update({
            'kpi_setting_dsm_lines_ids': kpi_lines,
            'kpi_setting_dsm_approval_lines_ids': [
                (0, 0, {
                    'employee_id': employee_dummy.id,
                })
            ]
        })
        department_obj = self.env['hr.department'].search([('department_level', '=', "DL3")])

        for dept in department_obj:
            self.department_ids = [(0, 0, {
                'department_id': dept.id,
                'dept_id': self.id,
            })]

    @api.depends('kpi_setting_dsm_lines_ids')
    def _sum_group_total(self):
        for rec in self:
            sum_total = 0
            sum_group_total = 0
            # master KPI
            for line in rec.kpi_setting_dsm_lines_ids:
                sum_group_total += line.weight_total
                # กลุ่มงานใน ตั้งค่า
                for group in line.kpi_group_lines_ids:
                    department_obj = self.env['hr.department'].search([('department_level', '=', "DL3")])
                    # กลุ่มงานใน hr
                    for dept in department_obj:
                        if group.kpi_group_department_id.id == dept.id:
                            sum_total += group.kpi_group_weight
            rec.group_weight = sum_group_total
            self.department_ids.update({
                'group_weight_total': sum_total
            })

    # @api.depends('kpi_setting_dsm_lines_ids.weight_total')
    # def _sum_group_total(self):
    #     for rec in self:
    #         sum_total = 0
    #         for line in rec.kpi_setting_dsm_lines_ids:
    #             sum_total += line.weight_total
    #         rec.group_weight = sum_total

    @api.depends('kpi_setting_dsm_lines_ids.kpi_weight')
    def _sum_kpi_weight_total(self):
        for rec in self:
            sum_total = 0
            for line in rec.kpi_setting_dsm_lines_ids:
                sum_total += line.kpi_weight
            rec.kpi_weight_total = sum_total

    def checkApproval(self):
        if len(self.kpi_setting_dsm_approval_lines_ids) <= 0:
            raise ValidationError(_('กรุณาระบุผู้อนุมัติรายการ KPI ก่อนส่งอนุมัติ'))

        for line in self.kpi_setting_dsm_approval_lines_ids:
            if line.employee_id.is_kpi_dummy:
                raise ValidationError(_('กรุณาผู้อนุมัติของคุณ ซึ่งจะต้องไม่ใช่ข้อมูล Dummy'))

    def checkLineStatus(self):
        if len(self.kpi_setting_dsm_lines_ids) <= 0:
            raise ValidationError(_('กรุณาสร้างข้อมูล Master KPI ก่อนส่งอนุมัติ'))

        for line in self.kpi_setting_dsm_lines_ids:
            if line.kpi_status == 'pending':
                raise ValidationError(_('คุณต้องอัพเดทข้อมูล KPI ให้เป็นข้อมูลที่ ดำเนินการแล้ว ทั้งหมด ก่อนส่งอนุมัติ'))

    def checkWeightTotal(self):
        if self.group_weight != 100:
            raise ValidationError(_('ค่าน้ำหนักรวมไม่เท่ากับทั้งหมดไม่เท่ากับ 100'))

    def action_sent_kpi_to_approve(self):
        self.checkApproval()
        self.checkLineStatus()
        # self.checkWeightTotal()

        if self.state == 'draft' or self.state == 'adjust':
            self.kpi_setting_dsm_approval_lines_ids[0].update({
                # 'approve_datetime': datetime.today(),
                'status': 'pending'
            })
            self.update({
                'current_approval_id': self.kpi_setting_dsm_approval_lines_ids[0].employee_id.user_id.id,
                'state': 'pending',
            })
            self.approve_count = 1

    def action_kpi_dsm_make_approval(self):
        return {
            'name': "Make Approval Wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'kpi_dsm_make_approval_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_kpi_setting_dsm_id': self.id,
                'default_current_state': self.state,
                # 'default_employee_id': employee_id.id,
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }


class kpi_setting_dsm_lines_models(models.Model):
    _name = 'kpi_setting_dsm_lines'

    kpi_setting_dsm_lines_id = fields.Many2one(
        "kpi_setting_dsm",
        required = True,
        ondelete='cascade'
    )
    kpi_master_lines_id = fields.Integer()
    kpi_code = fields.Char(
        string="รหัสตัวชี้วัด"
    )
    kpi_name = fields.Text(
        string="ชื่อตัวชี้วัด"
    )
    kpi_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 8)
    )
    kpi_bsc = fields.Char(
        string="มิติ"
    )
    # kpi_target = fields.Text(string='เป้าหมาย')
    # kpi_unit = fields.Many2one(
    #     'uom.uom',
    #     'หน่วย'
    # )
    kpi_status = fields.Selection(
        [
            ("pending", "รอดำเนินการ"),
            ("done", "ดำเนินการแล้ว"),
        ],
        string="สถานะ",
        compute='_depends_is_done',
        default="pending",
        store=True
    )
    kpi_definition = fields.Text(
        string="คำจำกัดความ"
    )
    kpi_calculate = fields.Selection(
        [
            ('sum', 'sum'),
            ('avg', 'average')
        ],
        string="คำนวณแบบ",
        default='sum'
    )
    kpi_budget = fields.Float(
        string="งบประมาณ",
        digits=(10, 2)
    )

    kpi_group_lines_ids = fields.One2many(
        'kpi_group_lines',
        'kpi_group_lines_id',
        required=True,
        copy=True
    )
    kpi_master_target_lines_ids = fields.Many2many(
        "kpi_target_lines",
        "kpi_setting_dsm_target_lines_rel",
        "kpi_setting_dsm_id",
        "kpi_target_lines_id",
        string='KPI Target',
        store=True,
    )
    kpi_master_definition_lines_ids = fields.Many2many(
        "kpi_definition_lines",
        "kpi_setting_dsm_definition_lines_rel",
        "kpi_setting_dsm_id",
        "kpi_definition_lines_id",
        string='KPI Definition',
        store=True,
    )
    # kpi_group_definition_line_ids = fields.One2many(
    #     "kpi_group_definition_lines",
    #     "kpi_group_definition_lines_id",
    #     string="KPI",
    #     copy=True
    # )
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
                rec.kpi_status = "done"
            else:
                rec.kpi_status = "pending"

    @api.depends('kpi_group_lines_ids')
    def _kpi_weight_total(self):
        for rec in self:
            sum = 0
            for line in rec.kpi_group_lines_ids:
                sum += line.kpi_group_weight
            rec.weight_total = sum

class kpi_master_group_lines(models.Model):
    _name = 'kpi_group_lines'

    kpi_group_lines_id = fields.Many2one(
        "kpi_setting_dsm_lines",
        required=True,
        ondelete='cascade'
    )
    kpi_group_department_id = fields.Many2one(
        "hr.department",
        string="กลุ่มงาน",
        domain="[('department_level', '=', 'DL3')]"
    )
    # kpi_group_name = fields.Selection(
    #     string="กลุ่มงาน",
    #     selection=[
    #         ('ศด', 'กลุ่มงานเศรษฐกิจดิจิทัล'),
    #         ('สก', 'กลุ่มงานสังคมและกำลังคนดิจิทัล'),
    #         ('คพ', 'กลุ่มงานโครงการพิเศษ'),
    #         ('ยศ', 'กลุ่มงานยุทธศาสตร์และบริหาร'),
    #         ('บห', 'กลุ่มงานบริหารสำนักงาน'),
    #         ('กส', 'กลุ่มงานกิจการสาขา'),
    #         ('GBDi', 'GBDi')
    #     ]
    # )
    kpi_group_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 4),
    )
    kpi_group_target = fields.Text(
        string="เป้าหมาย"
    )
    kpi_has_assistant = fields.Boolean(
        string="มี ชสศด.",
        default=False
    )
    kpi_assistant_employee_id = fields.Many2one(
        "hr.employee",
        string="ระบุ ชสศด."
    )
    kpi_group_definition_line_ids = fields.One2many(
        "kpi_group_definition_lines",
        "kpi_group_definition_lines_id",
        string="KPI",
        copy=True
    )

class kpi_group_definition_lines(models.Model):
    _name = 'kpi_group_definition_lines'

    kpi_group_definition_lines_id = fields.Many2one(
        "kpi_group_lines",
        required=True,
        ondelete='cascade'
    )
    kpi_group_def_level = fields.Integer(
        string="ระดับ"
    )
    kpi_group_def_name = fields.Text(
        string="คำจำกัดความ"
    )
    kpi_group_def_target = fields.Float(
        string="เป้าหมาย"
    )
    kpi_group_def_unit = fields.Many2one(
        'uom.uom',
        'หน่วย'
    )

class kpi_setting_dsm_approval_lines_models(models.Model):
    _name = 'kpi_setting_dsm_approval_lines'

    def _employee_filter(self):
        domain = []
        approval_ids = []
        group_id = self.env['res.groups'].search([('name', 'like', 'สามารถอนุมัติ KPI ระบบส่วนติดตามฯ')], limit=1)
        if group_id:
            if group_id.users:
                for user in group_id.users:
                    approval_ids.append(user.id)
            employee_dummy = self.env['hr.employee'].search([
                ('user_id', 'in', approval_ids)
            ])
            domain = [('id', 'in', employee_dummy.ids)]
        return domain

    kpi_setting_dsm_approval_lines_id = fields.Many2one(
        'kpi_setting_dsm',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string="ผู้อนุมัติ",
        domain=_employee_filter
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

class kpi_sum_department_lines(models.Model):
    _name = 'kpi_sum_department_lines'

    department_id = fields.Many2one(
        'hr.department',
        string="Department Name",
    )
    dept_id = fields.Many2one(
        'kpi_setting_dsm',
        string="department id",
        required=True,
    )
    group_weight_total = fields.Float(
        string='ค่าน้ำหนักรวม',
        readonly=True,
        digits=(10, 2),
    )







