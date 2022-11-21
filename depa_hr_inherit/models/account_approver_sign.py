# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from PIL import Image
import base64
import imagehash
import io
import hashlib

class account_approver_sign(models.Model):
    _name = 'account_approver_sign'

    position = fields.Selection(
        [
            ('P1', 'ผู้รับเงิน'),
            ('P2', 'ผู้จัดทำ'),
            ('P3', 'ผู้ตรวจสอบ'),
            ('P4', 'ผู้อนุมัติ')
        ],
        required=True,
        string="ตำแหน่ง"
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string="ผู้ลงลายเซ็น",
        required=True
    )

    is_used = fields.Boolean(
        string='กำลังใช้งาน',
        default=False
    )