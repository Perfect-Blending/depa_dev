import logging
from odoo import models

_logger = logging.getLogger(__name__)


class ReportFinReportXlsx(models.AbstractModel):
    _name = 'report.pfb_report_fin.report_fin_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        format = workbook.add_format({'font_size': 14})
        sheet = workbook.add_worksheet('Test')
        sheet.write(2, 0, 'fiscal_year', format)
        sheet.write(2, 1, 'group_id', format)
        sheet.write(2, 2, 'code', format)
        sheet.write(2, 3, 'name', format)
        sheet.write(2, 4, 'budget', format)
        sheet.write(2, 5, 'budget_reserve', format)
        sheet.write(2, 6, 'budget_return', format)
        sheet.write(2, 7, 'budget_spend', format)
        sheet.write(2, 5, 'budget_balance', format)
        sheet.write(2, 9, 'budget_balance_percent', format)
