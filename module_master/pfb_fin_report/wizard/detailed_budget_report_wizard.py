from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat


class DetailedBudgetWizard(models.TransientModel):
    _name = 'detailed.budget.report.wizard'

    fiscal_year = fields.Many2one('fw_pfb_fin_system_fiscal_year', string="Fiscal Year")
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
    )
    analytic_group = fields.Many2one(
        'account.analytic.group',
        string="Analytic Group",
    )
    year = fields.Char()
    analytic = fields.Char()

    @api.multi
    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref(
            'pfb_fin_report.action_report_detailed_budget_report_html')
        vals = action.read()[0]
        context = vals.get('context', {})
        if isinstance(context, pycompat.string_types):
            context = safe_eval(context)
        model = self.env['report.detailed.budget.report']
        report = model.create(self._prepare_detailed_budget_report())
        context['active_id'] = report.id
        context['active_ids'] = report.ids
        vals['context'] = context
        print(vals)
        return vals

    # @api.multi
    # def button_export_pdf(self):
    #     self.ensure_one()
    #     report_type = 'qweb-pdf'
    #     return self._export(report_type)

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        report_type = 'xlsx'
        return self._export(report_type)

    def _prepare_detailed_budget_report(self):
        self.ensure_one()
        return {
            'fiscal_year': self.fiscal_year.fiscal_year,
            'analytic_id': [(6, 0, self.analytic_id.ids)],
            'analytic_group': [(6, 0, self.analytic_group.ids,)]
        }

    def _export(self, report_type):
        model = self.env['report.detailed.budget.report']
        report = model.create(self._prepare_detailed_budget_report())
        return report.print_report(report_type)

    @api.onchange('fiscal_year')
    def _onchange_fiscal_year(self):
        if self.fiscal_year:
            self.year = self.fiscal_year.fiscal_year
            print(self.year)

