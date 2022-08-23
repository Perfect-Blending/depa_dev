from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError

class depa_welfare_basic_setting(models.Model):
    _name = 'depa_welfare_basic_setting'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        string='ปีงบประมาณ',
        default=_default_fiscal_year,
        required=True
    )
    start_date = fields.Date(
        string='วันที่เริ่มต้น',
        required=True
    )
    end_date = fields.Date(
        string='วันที่สิ้นสุด',
        required=True
    )
    show_sent_basic_button = fields.Boolean(
        string='แสดงปุ่มส่งเอกสาร',
        default=True
    )

    life_insurance_lines_ids = fields.One2many(
        "life_insurance_lines",
        "life_insurance_lines_id",
        required=True,
        copy=True
    )

    health_insurance_lines_ids = fields.One2many(
        "health_insurance_lines",
        "health_insurance_lines_id",
        required=True,
        copy=True
    )

    basic_welfare_attachment_lines_ids = fields.One2many(
        "basic_welfare_attachment_lines",
        "basic_welfare_attachment_lines_id",
        required=True,
        copy=True
    )

class basic_welfare_attachment_lines(models.Model):
    _name = 'basic_welfare_attachment_lines'

    name = fields.Char(
        string='ชื่อเอกสาร',
        required=True
    )
    basic_attachment_ids = fields.Many2many(
        "ir.attachment",
        "basic_welfare_attachment_lines_attachment_rel",
        "basic_welfare_attachment_lines_id",
        "ir_attachment_id",
        string='ไฟล์แนบ',
        required=True
    )
    active = fields.Boolean(
        string='เปิดใช้งาน',
        default=True
    )
    basic_welfare_attachment_lines_id = fields.Many2one(
        'depa_welfare_basic_setting',
        ondelete = 'cascade',
        required=True,
    )













