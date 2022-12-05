from datetime import datetime
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class NewStudentStatisticsReportWizard(models.TransientModel):
    _name = 'expenses.report.wizard.test'

    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date Range',
        required=True,
    )

    date_from = fields.Date(
        string='Date From',
    )

    date_to = fields.Date(
        string='Date To',
    )

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_range_id': self.date_range_id,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        return self.env.ref('expense_report.expense_report').report_action(self, data=data , config=False)

class NewStudentStatisticsReportWizard2(models.TransientModel):
    _name = 'expenses.report.wizard.test2'

    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date Range',
        required=True,
    )

    date_from = fields.Date(
        string='Date From',
    )

    date_to = fields.Date(
        string='Date To',
    )

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_range_id': self.date_range_id,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        return self.env.ref('expense_report.expense_report2').report_action(self, data=data , config=False)



