from odoo import api, fields, models


class SummaryBudgetReport(models.TransientModel):
    _name = 'report.summary.budget.report'
    _description = 'Balance Summary Budget Report'

    # Filters fields, used for data computation
    fiscal_year = fields.Char(string='Fiscal Year')
    analytic_group = fields.Many2many(
        comodel_name='account.analytic.group',
        string="Analytic Group",
    )
    analytic_id = fields.Many2many(
        comodel_name='account.analytic.account',
        string="Analytic Account",
    )
    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name='account.analytic.account',
        compute='_compute_results',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.analytic.account']
        print(Result,8888)
        domain = []
        if self.fiscal_year:
            domain += [('fiscal_year', '=', self.fiscal_year)]
        if self.analytic_id:
            domain += [('id', '=', self.analytic_id.id)]
        if self.analytic_group:
            group = []
            child = []
            name = []
            # Up
            for agc in self.analytic_group.children_ids:
                name.append(agc.name)
            for ag in self.analytic_group:
                name.append(ag.name)
                for uc in ag.parent_id:
                    name.append(uc.name)
                    for uc2 in uc.parent_id:
                        name.append(uc2.name)
                        for uc3 in uc2.parent_id:
                            name.append(uc3.name)

            # Down
                for ac in ag.children_ids:
                    child.append(ac.id)
                    for ac2 in ac.children_ids:
                        child.append(ac2.id)
                        for ac3 in ac2.children_ids:
                            child.append(ac3.id)
                group.append(ag.id)
                child.append(ag.id)
                test = sorted(child)
                print(test)
            domain += [('group_id', 'in', child)]
        self.results = Result.search(domain)
        print(self.results,99999)

    @api.multi
    def print_report(self, report_type='qweb'):
        self.ensure_one()
        action = report_type == 'xlsx' and self.env.ref(
            'pfb_fin_report.action_balance_summary_budget_report_xlsx') or \
                 self.env.ref('pfb_fin_report.action_detailed_budget_report_pdf')
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get('active_id'))
        if report:
            rcontext['o'] = report
            result['html'] = self.env.ref(
                'pfb_fin_report.summary_budget_report_html').render(
                rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
