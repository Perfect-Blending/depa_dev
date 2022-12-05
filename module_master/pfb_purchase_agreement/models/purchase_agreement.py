# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class PurchaseRrequisition(models.Model):
    _inherit = 'purchase.requisition'

    bg_amount = fields.Float(
        string='เงินประกันสัญญา',
        required=True)
    bg_note = fields.Text(
        string="รายละเอียดเงินประกันสัญญา",
        required=True)
    bg_date = fields.Date(
        string='วันที่บันทึกข้อความ',
        required=True)
    project_code = fields.Char(
        string="รหัสโครงการ",
        )
    project_name = fields.Char(
        string="ชื่อโครงการ",
        )
