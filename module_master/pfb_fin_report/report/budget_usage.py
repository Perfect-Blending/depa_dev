from odoo import api, fields, models


class BudgetUsageReport(models.TransientModel):
    _name = 'report.budget.usage.report'
    _description = 'Budget Usage Report'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Requester",
    )
    date_from = fields.Date(
        string='Date From',
    )

    date_to = fields.Date(
        string='Date To',
    )
    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name='fw_pfb_fin_system_100',
        compute='_compute_results',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['fw_pfb_fin_system_100']
        print(Result)
        domain = []
        print(self.date_from)
        print(self.date_to)
        print(self.employee_id)
        if self.date_from:
            print(1)
            domain += [('fin_date', '>=', self.date_from)]
        if self.date_to:
            print(1)
            domain += [('fin_date', '<=', self.date_to),  ('state', 'not in', ['draft', 'cancelled'])]
        if self.employee_id:
            print(1)
            domain += [('requester', '=', self.employee_id.id)]

        self.results = Result.search(domain)
        print(self.results, '444444')

    @api.multi
    def print_report(self, report_type='qweb'):
        self.ensure_one()
        action = report_type == 'xlsx' and self.env.ref(
            'pfb_fin_report.action_budget_usage_report_xlsx') or \
                 self.env.ref('pfb_fin_report.action_budget_usage_report_pdf')
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get('active_id'))
        print(report)
        if report:
            rcontext['o'] = report
            result['html'] = self.env.ref(
                'pfb_fin_report.report_budget_usage_report_html').render(
                rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
