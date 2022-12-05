from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat


class BudgetUsageWizard(models.TransientModel):
    _name = 'budget.usage.report.wizard'

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

    @api.multi
    def button_export_html_usage(self):
        self.ensure_one()
        action = self.env.ref(
            'pfb_fin_report.action_report_budget_usage_report_html')
        vals = action.read()[0]
        context = vals.get('context', {})
        if isinstance(context, pycompat.string_types):
            context = safe_eval(context)
        model = self.env['report.budget.usage.report']
        report = model.create(self._prepare_budget_usage_report())
        context['active_id'] = report.id
        context['active_ids'] = report.ids
        vals['context'] = context
        print(vals)
        return vals

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        report_type = 'xlsx'
        return self._export(report_type)

    def _prepare_budget_usage_report(self):
        self.ensure_one()
        return {
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

    def _export(self, report_type):
        model = self.env['report.budget.usage.report']
        report = model.create(self._prepare_budget_usage_report())
        return report.print_report(report_type)


