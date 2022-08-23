from odoo import models, fields, api

class source_master(models.Model):
    _name = "source_master"

    name = fields.Char(
        string="ที่มางบประมาณ"
    )