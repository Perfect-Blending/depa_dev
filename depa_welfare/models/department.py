
from odoo import fields, models


class Department(models.Model):
    _inherit = 'hr.department'

    # depa_department = fields.Char(string='ชื่อย่อหน่วยงาน')
    # depa_phone = fields.Char(string='โทรศัพท์')
    # depa_fax = fields.Char(string='โทรสาร')
    # depa_email = fields.Char(string='อีเมล์')
    # depa_document_sequence = fields.Char(string='คำนำหน้าหนังสือภายนอก')
    is_gbdi = fields.Boolean(
        string="Is GBDi",
        default=False,
    )
