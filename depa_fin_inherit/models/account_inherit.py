from datetime import date
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class account_inherit(models.Model):
    _inherit = 'account.invoice'

    code_ref = fields.Char(
        string="เลขที่ใบเสร็จ",
    )