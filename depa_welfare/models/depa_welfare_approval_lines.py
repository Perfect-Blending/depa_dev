from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
APPROVAL_STATE = [
    ('pending', 'รออนุมัติ'),
    ('approved', 'อนุมัติแล้ว'),
    ('rejected', 'ปฎิเสธ'),
    ('cancel', 'ยกเลิก'),
    ('adjust', 'ปรับแก้ไข'),
    ('rechecked', 'ตรวจสอบอีกครั้ง'),
]

class depa_welfare_approval_lines(models.Model):
    _name = 'depa_welfare_approval_lines'

    depa_welfare_approval_lines_id = fields.Many2one(
        'depa_welfare'
    )

    process_setting_id = fields.Many2one(
        'workflow_process_setting'
    )

    process_step = fields.Integer(
        string="ขั้นตอน"
    )

    process_approval = fields.Many2one(
        'hr.employee',
        string="ผู้อนุมัติ"
    )

    process_approval_position = fields.Char(
        string="ตำแหน่ง"
    )

    remark = fields.Text(
        string="ความคิดเห็น",
        help="กรอกเพื่อแสดงความคิดเห็น",
    )

    status = fields.Selection(
        APPROVAL_STATE,
        string = "สถานะ"
    )

    on_date = fields.Datetime(
        # default=datetime.now(),
        string="วัน/เวลาที่อนุมัติ"
    )

class depa_welfare_approval_lines_history(models.Model):
    _name = 'depa_welfare_approval_lines_history'

    approval_lines_id = fields.Many2one(
        'depa_welfare_approval_lines'
    )

    remark_history = fields.Text(
        string="ความคิดเห็น"
    )

    status_history = fields.Selection(
        APPROVAL_STATE,
        string="สถานะ"
    )

    on_date_history = fields.Datetime(
        string="วัน/เวลาที่อนุมัติ"
    )

