from odoo import models, fields, api, _


class WorkAcceptanceInherit(models.Model):
    _inherit = 'work.acceptance'

    check_date = fields.Datetime(string="คณะกรรมการตรวจรับวันที่")
    select_check = fields.Selection([('cw1', 'ถูกต้อง ครบถ้วนตามสัญญา'),
                                     ('cw2', 'ถูกต้อง ครบถ้วนตามสัญญา แต่ '
                                             'ผู้ขาย/ผู้รับจ้าง/ที่ปรึกษาส่งมอบเกินกำหนดเวลา'),
                                     ('cw3', 'อื่นๆ')], string="เงื่อนไข")
    date_check = fields.Integer(string="จำนวนวัน")
    fines = fields.Integer(string="จำนวนเงินค่าปรับทั้งสิ้น")
    notes_check = fields.Char(string="หมายเหตุ")


