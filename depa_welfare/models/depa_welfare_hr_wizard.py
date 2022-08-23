from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import date

class depa_welfare_hr_wizard(models.TransientModel):
    _name = 'depa_welfare_hr_wizard'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        required=True
    )

    employee = fields.Char()
    name = fields.Char()
    employee_ids = fields.One2many(
        'depa_welfare_hr_lines',
        'hr_employee_id',
        string='Employee',
        required=True,
        copy=True
    )
    is_create = fields.Boolean(default=True)

    @api.onchange('is_create')
    def _onchange_is_create(self):
        if self.is_create:
            fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
                ('date_start', '<=', date.today()),
                ('date_end', '>=', date.today()),
            ], limit=1)
            #print(self.is_create)
            #print(fiscal_year_obj.id)
            depa_welfare_hr = self.env['depa_welfare_hr'].search([
                ('year', '=', fiscal_year_obj.id)
            ])

            #self.employee_ids = self.env['depa_welfare_hr_lines'].search([('hr_employee_id', '=', depa_welfare_hr.id)])
            employee_obj = self.env['hr.employee'].search([])
            for emp in employee_obj:
                self.employee_ids = [(0, 0, {
                    'employee_id': emp.id,
                    'hr_employee_id': self.id,
                })]
            #print(self.employee_ids)







    # class SettingLine(models.Model):
    #     _name = 'depa_welfare_hr_lines'
    #
    #     employee_id = fields.Many2one(
    #         'hr.employee',
    #         string="Employee Name"
    #     )
    #     point = fields.Char()
    #     hr_employee_id = fields.Many2one(
    #         'depa_welfare_hr',
    #         string="Document id"
    #     )



