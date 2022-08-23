from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class vaccine_setting(models.Model):
    _name = 'vaccine_setting'

    vaccine_name = fields.Text(string='ชื่อวัคซีน')

    def name_get(self):
        return [(rec.id, rec.vaccine_name) for rec in self]