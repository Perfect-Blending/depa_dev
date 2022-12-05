from datetime import datetime
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from dateutil.relativedelta import relativedelta


class ExpensesReportWizard(models.AbstractModel):
    _name = 'report.expense_report.expense_report_view'

    def _convert_date_to_bhuddhist(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.model
    def _get_report_values(self, docids, data=None):
        date_range_id_test = data['form']['date_range_id']
        date_from_test = data['form']['date_from']
        date_to_test = data['form']['date_to']
        date_test = date_to_test[9:10]
        print(date_from_test, date_test)
        docs = self.env['hr.expense'].search([
            ('date', '<=', date_to_test),
            ('date', '>=', date_from_test),
            ('payment_mode', '=', 'petty_cash'),
            ('state', '=', 'done')
        ], order='id')
        init_balance = 0
        for doc in docs:
            init_balance += doc.total_amount
            date = doc.date
            yaer = int((date).strftime('%Y')) + 543

        return {
            'doc_ids': docs.ids,
            'doc_model': 'hr.expense',
            'docs': docs,
            'date_from_test': date_from_test,
            'date_to_test': date_to_test,
            'date': date,
            'init_balance': init_balance,
            'yaer': yaer,
        }


class ExpensesReportWizard2(models.AbstractModel):
    _name = 'report.expense_report.expense_report_view2'

    def _convert_date_to_bhuddhist(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.model
    def _get_report_values(self, docids, data=None):
        date_range_id_test = data['form']['date_range_id']
        date_from_test = data['form']['date_from']
        date_to_test = data['form']['date_to']
        docs = self.env['hr.expense'].search([
            ('date', '<=', date_to_test),
            ('date', '>=', date_from_test),
            ('state', '=', 'done')
        ], order='id')
        init_balance = 0
        for doc in docs:
            number = doc.reference
            obj = self.env['fw_pfb_fin_system_401'].search([
                ('fin_no', '=', number),
            ])
            number_fin = obj.fin_no
            date_activity = obj.activity_end_date
            date_end = obj.fin_end_date
            init_balance += doc.total_amount
            date = doc.date
            date_tb = self._convert_date_to_bhuddhist(doc.date)
            date_sheet = self._convert_date_to_bhuddhist(doc.sheet_id.accounting_date)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'hr.expense',
            'docs': docs,
            'date_from_test': date_from_test,
            'date_to_test': date_to_test,
            'date': date,
            'date_tb': date_tb,
            'init_balance': init_balance,
            'date_sheet': date_sheet,
            'date_activity': date_activity,
            'date_end': date_end,
            'obj': obj,
        }
