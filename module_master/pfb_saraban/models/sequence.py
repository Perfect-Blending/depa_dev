from odoo import fields, models


class hr(models.Model):
    _inherit = 'ir.sequence'
    sarabun_active = fields.Boolean(
        'Use with sarabun',
        default=False
    )
    circular_letter = fields.Boolean(
        string='หนังสือเวียน',
        default=False,
        required=True
    )
    receive_document = fields.Boolean(
        string='หนังสือรับ',
        default=False,
        required=True
    )
    document_type = fields.Selection([
        ('บันทึกข้อความ', 'บันทึกข้อความ'),
        ('คำสั่ง ก', 'คำสั่ง ก'),
        ('คำสั่ง ข', 'คำสั่ง ข'),
        ('คำสั่ง ค', 'คำสั่ง ค'),
        ('คำสั่ง พ', 'คำสั่ง พ'),
        ('ระเบียบ', 'ระเบียบ'),
        ('ประกาศ', 'ประกาศ'),
        ('ประกาศพัสดุ', 'ประกาศพัสดุ'),
        ('ข้อบังคับ', 'ข้อบังคับ'),
        ('หนังสือภายนอก+หนังสือรับรอง',
         'หนังสือภายนอก+หนังสือรับรอง'),
    ],
        copy=False,
        string="Document type")
    department_id = fields.Many2one('hr.department', string="Department id")
    department_name = fields.Char(
        string="Department name", related="department_id.name", readonly=True)
