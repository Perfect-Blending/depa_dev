from odoo import models, fields, api, _
from odoo.osv import expression


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"

    sign_img = fields.Binary(
        string='e-signature'
    )
