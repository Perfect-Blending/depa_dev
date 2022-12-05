from odoo import models, fields, api, _


class AccountAnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'
    _rec_name = 'fiscal_year'

    date_start = fields.Date(string='Start Period',)
    date_to = fields.Date(string='End Period',)
    project_type = fields.Selection(string='Project Type',
                                   selection=[('new', 'New projects'), ('old', 'Continue projects')], )

    department = fields.Many2one('hr.department', string='Department')
    manager = fields.Many2one('hr.employee', string='Manager')
    manager_co = fields.Many2one('hr.employee', string='Manager (Co)')
    coordinator = fields.Many2one('hr.employee', string='Coordinator')
    principle_and_reason = fields.Char(string='Principle And Reasons')
    objective = fields.Char(string='Objective')
    target_project = fields.Char(string='Target Project')
    target_group = fields.Char(string='Target Group')
    operation_area = fields.Char(string='Operation Area')
    impact_and_benefit = fields.Char(string='The Impact And Benefits')
    earn_income_plan = fields.Char(string='Earn Income Plan')
    partners = fields.Char(string='Partners')

    budget = fields.Float()
    budget_spend = fields.Float(compute='_budget_spend')
    budget_balance = fields.Float()
    # budget_balance_percent = fields.Float(compute='_balance_percent_compute')
    budget_balance_percent = fields.Float()

    fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        compute='_compute_group_id',
        string='Fiscal Year',
        store=True,
    )

    # Allow Negative budget work with allow negative access rights flag
    allow_negative = fields.Boolean(
        string='Allow Negative',
        default=False,
    )

    @api.one
    def _budget_spend(self):
        for budget in self:
            self.budget_spend = self.budget - self.budget_balance


    @api.onchange('group_id')
    def _onchange_group_id(self):
        self.fiscal_year = None
        if self.group_id.fiscal_year:
            self.fiscal_year = self.group_id.fiscal_year.id

    @api.multi
    @api.depends('group_id.fiscal_year')
    def _compute_group_id(self):
        for aa in self:
            if aa.group_id:
                aa.fiscal_year = aa.group_id.fiscal_year.id

    # @api.depends('budget', 'budget_balance')
    # def _balance_percent_compute(self):
    #     if self.budget_balance != 0:
    #         self.budget_balance_percent = (self.budget_balance/self.budget) * 100

class AccountAnalyticGroupInherit(models.Model):
    _inherit = 'account.analytic.group'

    fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        string='Fiscal Year',
    )

    @api.onchange('fiscal_year')
    def _onchange_fiscal_year_id(self):
        return {'domain': { 'parent_id': [('fiscal_year', '=', self.fiscal_year.id if self.fiscal_year else None)]}}

    @api.multi
    def name_get(self):
        def get_names(cat):
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]


class fw_pfb_fin_fiscal_year(models.Model):
    _name = 'fw_pfb_fin_system_fiscal_year'
    _rec_name = 'fiscal_year'

    fiscal_year = fields.Char(
        string='Fiscal Year',
        required=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.onchange('active')
    def _onchange_active(self):
        aac = self.env['account.analytic.account'].search([
            ('fiscal_year.fiscal_year', '=', self.fiscal_year),
            '|',
            ('active', '=', True),
            ('active', '=', False)
        ])
        for aa in aac:
            aa.write({'active': self.active})

    @api.multi
    def name_get(self):
        res = []
        for obj in self:
            name = obj.fiscal_year
            res.append((obj.id, name))
        return res
