# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from PIL import Image
import base64
import imagehash
import io
import hashlib

class hr_employee_inherit(models.Model):
    _inherit = 'hr.employee'

    depa_job_level = fields.Selection(
        [
            ('L1', 'เจ้าหน้าที่ระดับ 1'),
            ('L2', 'เจ้าหน้าที่ระดับ 2'),
            ('L3', 'เจ้าหน้าที่ระดับ 3'),
            ('L4', 'เจ้าหน้าที่อาวุโส'),
            ('L5', 'ผู้เชี่ยวชาญอาวุโส'),
            ('L6', 'ผู้จัดการสาขา/ส่วน'),
            ('L7', 'ผู้อำนวยการฝ่าย'),
            ('L8', 'ผู้ช่วยผู้อำนวยการ'),
            ('L9', 'รองผู้อำนวยการ'),
            ('L10', 'ผู้อำนวยการสำนักงาน')
        ],
        string="ระดับ"
    )
    depa_job_class = fields.Selection(
        [
            ('C1', 'ขั้น 1'),
            ('C2', 'ขั้น 2'),
            ('C3', 'ขั้น 3'),
            ('C4', 'ขั้นอาวุโส'),
        ],
        string="ขั้น"
    )
    buddy = fields.Many2one(
        'hr.employee',
        string="Buddy"
    )

    # certificate = fields.Selection(
    #     [
    #         ('Bachelor', 'ปริญญาตรี'),
    #         ('Master', 'ปริญญาโท'),
    #         ('Doctoral', 'ปริญญาเอก'),
    #     ],
    # )

    address_home_1 = fields.Text(
        string="ที่อยู่ปัจจุบัน 1"
    )
    address_lat_1 = fields.Text(
        string="ละติจูด"
    )
    address_lon_1 = fields.Text(
        string="ลองติจูด"
    )
    address_home_2 = fields.Text(
        string="ที่อยู่ปัจจุบัน 2"
    )
    address_lat_2 = fields.Text(
        string="ละติจูด"
    )
    address_lon_2 = fields.Text(
        string="ลองติจูด"
    )
    employee_vaccine_ids = fields.One2many(
        "hr_employee_vaccine",
        "employee_vaccine_id"
    )
    employee_hold_ids = fields.One2many(
        "hr_employee_hold",
        "employee_hold_id"
    )
    employee_certificate_ids = fields.One2many(
        "hr_employee_certificate",
        "employee_certificate_id"
    )

    bg_card = fields.Binary(
        string='พื้นหลัง'
    )
    nickname = fields.Text(
        string="ชื่อเล่น"
    )
    name_en = fields.Text(
        string="ชื่อภาษาอังกฤษ"
    )
    duration = fields.Char(
        string='ระยะเวลาทำงาน',
        compute='_compute_duration'
    )
    job_title_en = fields.Text(
        compute='_compute_job',
        string='ตำแหน่ง EN',
    )
    department_en = fields.Char(
        compute='_compute_dept',
        string='แผนก EN',
    )
    font_color_card = fields.Selection(
        [
            ('#ffffff', 'white'),
            ('#000000', 'black'),
            ('#fff200', 'yellow'),
            ('#ffc600', 'orange'),
            ('#0c2f53', 'blue')
        ],
        string="สี Font",
        default='#0c2f53'
    )
    bg_color_card = fields.Selection(
        [
            ('#000000', 'black'),
            ('#fff200', 'yellow'),
            ('#ffc600', 'orange'),
            ('#0c2f53', 'blue'),
            ('#eaeaea', 'grey')
        ],
        string="สี Background",
        default='#0c2f53'
    )
    menu_color_card = fields.Selection(
        [
            ('#000000', 'black'),
            ('#fff200', 'yellow'),
            ('#ffc600', 'orange'),
            ('#0c2f53', 'blue'),
            ('#999999', 'grey')
        ],
        string="สีเมนู",
        default='#fff200'
    )
    entrance_qr_code = fields.Binary(
        string="QR Code"
    )


    @api.depends("job_id")
    def _compute_job(self):
        self.job_title_en = self.job_id.name_en

    @api.depends("department_id")
    def _compute_dept(self):
        self.department_en = self.department_id.name_en


    @api.depends('pass_probation_date')
    def _compute_duration(self):
        try:
            self.duration = str(self.get_duration_from_dob(self.pass_probation_date))
        except:
            self.duration = ''

    def get_duration_from_dob(self, dob):
        duration = relativedelta(date.today(), dob)
        return f"{duration.years} ปี {duration.months} เดือน {duration.days} วัน"

    @api.onchange('sign_img')
    def _check_hash_img(self):
        if self.sign_img:
            employee = self.env['hr.employee'].search([('emp_code', "=", self.emp_code)], limit=1)
            signature = self.env['hr_employee_signature_setting'].search(
                [('employee_id', '=', employee.id), ('active', '=', True)]
            ,limit=1)
            if signature:
                image = base64.b64decode(self.sign_img)
                img = Image.open(io.BytesIO(image))
                hashed = imagehash.average_hash(img)
                salt = str(self.emp_code).encode()
                hashed_text = str(hashed).encode()
                digest = hashlib.pbkdf2_hmac('sha256', hashed_text, salt, 10000)
                if str(digest.hex()) != str(signature.hash_signature):
                    self.sign_img = False
                    raise ValidationError(_(f"รหัสของภาพลายเซ็นไม่ตรงกับที่ตั้งค่าไว้ | {digest.hex()}"))
            else:
                raise ValidationError(_("กรุณาตั้งค่ารหัสลายเซ็นของท่านให้เรียบร้อย "))

class hr_employee_vaccine(models.Model):
    _name = 'hr_employee_vaccine'

    employee_vaccine_id = fields.Many2one(
        "hr.employee"
    )
    needle_id = fields.Integer(
        string="เข็ม",
        required=True,
        default=1
    )
    vaccine_name = fields.Many2one(
        "vaccine_setting",
        string="ชื่อวัคซีน",
        required=True
    )
    vaccine_date = fields.Date(
        string="วันที่ฉีดวัคซีน",
        required=True
    )
    vaccine_location = fields.Text(
        string="สถานที่"
    )

class hr_employee_hold(models.Model):
    _name = 'hr_employee_hold'

    employee_hold_id = fields.Many2one(
        "hr.employee"
    )
    assets_name = fields.Text(
        string="ชื่อสินทรัพย์"
    )
    product_code = fields.Text(
        string="รหัสสินทรัพย์"
    )
    date_start = fields.Date(
        string="วันที่ครอบครอง"
    )
    date_end = fields.Date(
        string="วันที่สิ้นสุด"
    )

class hr_employee_certificate(models.Model):
    _name = 'hr_employee_certificate'

    employee_certificate_id = fields.Many2one(
        "hr.employee"
    )
    certificate_attachment_id = fields.Many2one(
        'hr_employee_certificate'
    )
    certificate_attachment_ids = fields.Many2many(
        'ir.attachment',
        'certificate_attachment_rel',
        'certificate_attachment_id',
        'ir_attachment_id',
        string='เอกสารแนบ',
        # required=False,
    )
    description = fields.Text(
        required=True,
        string='รายละเอียด'
    )
    start_date = fields.Date(string="วันที่เริ่มต้น")
    end_date = fields.Date(string="วันที่สิ้นสุด")

class hr_employee_signature_setting(models.Model):
    _name = 'hr_employee_signature_setting'

    employee_id = fields.Many2one(
        'hr.employee',
        required=True
    )

    hash_signature = fields.Text(
        required=True
    )

    active = fields.Boolean(
        default=True
    )

