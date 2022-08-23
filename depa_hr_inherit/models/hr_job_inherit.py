
from odoo import fields, models


class Hrjob(models.Model):
    _inherit = 'hr.job'

    name_en = fields.Char(
        string="ตำแหน่ง EN"
    )
