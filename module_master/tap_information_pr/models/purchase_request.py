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
    middle_price = fields.Many2many("ir.attachment",
                                    "attachment_middle_price_rel",
                                    "attachment_middle_price_id",
                                    "attachment_id",
                                    string="Attribute")
    attribute_pr = fields.Many2many("ir.attachment",
                                    "attachment_attribute_pr_rel",
                                    "attachment_attribute_pr_id",
                                    "attachment_id",
                                    string="Attribute")
    attribute_pr2 = fields.Many2many("ir.attachment",
                                     "attachment_attribute_pr2_rel",
                                     "attachment_attribute_pr2_id",
                                     "attachment_id",
                                     string="Attribute")
    attribute_pr3 = fields.Many2many("ir.attachment",
                                     "attachment_attribute_pr3_rel",
                                     "attachment_attribute_pr3_id",
                                     "attachment_id",
                                     string="Attribute")
