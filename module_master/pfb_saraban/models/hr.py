from odoo import models, fields, api, _


class Department(models.Model):
    _inherit = "hr.department"
    _rec_name = 'name'
