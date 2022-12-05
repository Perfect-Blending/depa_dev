from odoo import models, fields, api, _


class AccountAnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'

    date_start = fields.Date(string='Start Period',)
    date_to = fields.Date(string='End Period',)
    project_new = fields.Selection(string='Project Type',
                                   selection=[('new', 'New projects'), ('old', 'Continue projects')], )

    department_pb = fields.Many2one('hr.department', string='Department')
    customer_pb = fields.Many2one('hr.employee', string='Manager')
    customer2_pb = fields.Many2one('hr.employee', string='Manager (Co)')
    customer3_pb = fields.Many2one('hr.employee', string='Coordinator')
    notes1 = fields.Char(string='Principle And Reasons')
    notes2 = fields.Char(string='Objective')
    notes3 = fields.Char(string='Target Project')
    notes4 = fields.Char(string='Target Group')
    notes5 = fields.Char(string='Operation Area')
    notes6 = fields.Char(string='The Impact And Benefits')
    notes7 = fields.Char(string='Earn Income Plan')
    notes8 = fields.Char(string='Partners')




