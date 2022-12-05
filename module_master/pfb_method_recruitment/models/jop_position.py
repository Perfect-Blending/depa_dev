from odoo import models, fields, api, _


class JopPositionWork(models.Model):
    _name = 'jop.position.work'
    _description = 'Jop Position Work'
    _rec_name = 'jop_work'


    jop_work = fields.Char(string='Jop Position', required=True)








