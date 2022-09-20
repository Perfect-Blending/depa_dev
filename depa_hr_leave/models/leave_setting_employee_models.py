# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime

class leave_setting_employee(models.Model):
    _name = 'leave_setting_employee'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        string='ปีงบประมาณ',
        required=True
    )
    employee_ids = fields.One2many(
        'leave_setting_employee_lines',
        'hr_employee_id',
        string='รายชื่อพนักงาน',
    )
    is_create = fields.Boolean(default=True)

    @api.onchange('is_create')
    def _onchange_is_create(self):
        if self.is_create:

            employee_obj = self.env['hr.employee'].search([])

            for emp in employee_obj:
                self.employee_ids = [(0, 0, {
                    'employee_id': emp.id,
                    'hr_employee_id': self.id,
                    'sick': 30.0,
                    'site': 30.0,
                    'checkin': 30.0,
                    'seminar': 30.0
                })]

class leave_setting_employee_lines(models.Model):
    _name = 'leave_setting_employee_lines'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )

    hr_employee_id = fields.Many2one(
        'leave_setting_employee',
        string="hr id",
        required=True,
    )
    sick = fields.Float(
        string="ลาป่วย",
    )
    personal = fields.Float(
        string="ลากิจ",
    )
    vacation = fields.Float(
        string="ลาพักผ่อน",
    )
    vacation_remaining = fields.Float(
        string="ลาพักผ่อน (ยกยอด)"
    )
    site = fields.Float(
        string="ปฏิบัติงานนอกสถานที่",
    )
    checkin = fields.Float(
        string="ลืมลงเวลาเข้า",
        default=365.0
    )
    seminar = fields.Float(
        string="อบรม/สัมมนา",
    )
    birth = fields.Float(
        string="ลาคลอดบุตร",
    )
    raising = fields.Float(
        string="ลาเลี้ยงดูบุตร",
    )
    ordain = fields.Float(
        string="ลาอุปสมบท/ลาไปประกอบพิธีฮัจญ์",
    )
    training = fields.Float(
        string="ลาเพื่อประโยชน์ในการพัฒนาพนักงาน",
    )
    government = fields.Float(
        string="ลาตามที่มติคณะรัฐมนตรีกำหนด",
    )

