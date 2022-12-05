from odoo import fields, models


class TapPurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    method_of_recruitment = fields.Many2one('method.recruitment', 'Method of recruitment')
    date_pr = fields.Date(string="Date")
    select_check = fields.Selection([('pr1', 'ราคากลาง กรณีงบประมาณในการจัดซื้อจัดจ้างเกินหนึ่งแสนบาท'),
                                     ('pr2', 'ขอบเขตของงานหรือคุณลักษณะเฉพาะ'),
                                     ('pr3', 'รายชื่อคณะกรรมการต่างๆ'),
                                     ('pr4', 'บันทึกอนุมัติหลักการ')
                                     ], string="มีเอกสารแนบมาด้วย")
    notes_check = fields.Char(string="จำนวนชุดเอกสาร")
    pr_ck = fields.Boolean(string='ราคากลาง กรณีงบประมาณในการจัดซื้อจัดจ้างเกินหนึ่งแสนบาท')
    pr2_ck = fields.Boolean(string='ขอบเขตของงานหรือคุณลักษณะเฉพาะ')
    pr3_ck = fields.Boolean(string='รายชื่อคณะกรรมการต่างๆ')
    pr4_ck = fields.Boolean(string='บันทึกอนุมัติหลักการ')
    pr_test_on = fields.Char(string="5555555555555")
