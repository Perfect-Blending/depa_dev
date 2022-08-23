# -*- coding: utf-8 -*-

from odoo import models, fields, api

class welfare_types(models.Model):
    _name = 'depa_welfare_types'

    name = fields.Char(
        string="ชื่อสวัสดิการ",
        required=True
    )
    limit_point =  fields.Integer(
        string="Limit คะแนน (ต่อปี)"
    )
    limit_amount = fields.Float(
        string="Limit จำนวนเงิน (ต่อปี)"
    )
    full_multiply = fields.Float(
        string="ตัวคูณ"
    )
    half_multiply = fields.Float()
    is_half_full = fields.Boolean(
        string="ตัวคูณคะแนน"
    )
    is_depa_only = fields.Boolean(
        string="เฉพาะพนักงาน depa"
    )
    for_family = fields.Boolean(
        string="สำหรับครอบครัว"
    )
    more_one_items = fields.Boolean(
        string="มากกว่า 1 รายการ"
    )
    family_relation = fields.Selection(
        selection=[
            ('FA-MO', 'บิดา-มารดา'),
            ('SP', 'คู่สมรส'),
            ('CH', 'บุตร'),
        ],
        string="ความสัมพันธ์"
    )
    family_age = fields.Boolean(
        string="กำหนดอายุ"
    )
    family_age_from = fields.Integer(
        string="อายุเริ่มต้น"
    )
    family_age_to = fields.Integer(
        string="อายุสิ้นสุด"
    )
    active = fields.Boolean(
        string="สถานะ",
        default=True
    )
    depa_welfare_type_lines_ids = fields.One2many(
        "depa_welfare_type_lines",
        "depa_welfare_type_lines_id"
    )
