
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError


class report_fin(models.Model):
    # _name = 'report_fin'
    _inherit = 'account.analytic.account'

    # def _default_fiscal_year(self):
    #     fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
    #         ('date_start', '<=', date.today()),
    #         ('date_end', '>=', date.today()),
    #     ], limit=1)
    #
    #     return fiscal_year_obj.id

    fin100_project_ids = fields.One2many('fw_pfb_fin_system_100_projects', 'projects_and_plan', 'FIN EXPENSE LINES')

    sum_reserve_fin_100 = fields.Float(
        string="ยอดกันงบประมาณ",
        compute="_get_fin100"
    )

    payment_201 = fields.Float(
        string="ยอดเบิกจ่าย",
        compute="_get_fin100"
    )
    sum_balance = fields.Float(
        string="ยอดคงเหลือ/รอปิด Fin100",
        compute="_get_fin100"
    )

    sum_balance = fields.Float(
        string="ยอดคงเหลือ/รอปิด Fin100",
        compute="_get_fin100"
    )

    total_budget = fields.Float(
        string="ยอดคงเหลือของงบประมาณ",
        compute="_get_fin100"
    )

    @api.depends('fiscal_year')
    def _get_fin100(self):
        for res in self:
            sum_fin100 = 0
            payment_201 = 0
            # print(res.id)
            line_proj = res.env['fw_pfb_fin_system_100_projects'].search([
                ('projects_and_plan', '=', res.id)
            ])
            line_100 = res.env['fw_pfb_fin_system_100_line'].search([
                ('projects_and_plan', '=', res.id)
            ])
            for fin100 in line_100:
                line_201 = res.env['fw_pfb_fin_system_201_line'].search([
                    ('fin_line_id', '=', fin100.id)
                ])
                for fin201 in line_201:
                    payment_201 += fin201.payment_amount

            res.payment_201 = payment_201

            for line in line_proj:
                if (line.fin100_state == "completed"):
                    sum_fin100 += line.projects_reserve

            res.sum_reserve_fin_100 = sum_fin100
            res.sum_balance = sum_fin100 - payment_201
            res.total_budget = res.budget - payment_201





