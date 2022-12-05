import logging
from odoo import models

_logger = logging.getLogger(__name__)


class ReportDetailedBudgetReportXlsx(models.AbstractModel):
    _name = 'report.pfb_fin_report.report_detailed_budget_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        border = workbook.add_format({
            'border': 2,
            'border_color': '#000000',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D7E4BC',

        })
        border2 = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'valign': 'vcenter',
        })
        sheet = workbook.add_worksheet('รายงานงบประมาณแบบละเอียด')
        sheet.set_column('B:H', 15, )
        name = []
        name2 = []
        name_id = []
        array_group = []
        count_row = 0
        count_row2 = 0
        count_aa = 0
        col_name = 3
        code_name = ''
        for co in objects.results.sorted(key=lambda r: r.id):
            if co.group_id not in array_group:
                array_group.append(co.group_id)
        for ga in sorted(array_group):
            sheet.write(col_name, 1, ga.complete_name)
            for result in objects.results:
                if array_group[count_aa] == result.group_id:
                    col_name += 1
                    code_name = result.code + '-' + result.name
                    sum_residual = 0
                    sum_reserve = 0
                    sum_return = 0
                    sum_residual_amount = 0

                    sheet.write(col_name, 2, code_name)
                    col_name += 1
                    sheet.write(col_name, 1, 'Fin100 Date', border)
                    sheet.write(col_name, 2, 'Fin100', border)
                    sheet.write(col_name, 3, 'Residual', border)
                    sheet.write(col_name, 4, 'Reserve', border)
                    sheet.write(col_name, 5, 'Return', border)
                    sheet.write(col_name, 6, 'Residual Amount', border)
                    sheet.write(col_name, 7, 'Fin100 Status', border)
                    col_name += 1
                    for fin100_project in result.fin100_project_ids:
                        sum_reserve += fin100_project.projects_reserve
                        sum_return += fin100_project.projects_return
                        sum_residual_amount += fin100_project.projects_residual_amount

                        sheet.write(col_name, 1, fin100_project.fin100_date, border2)
                        sheet.write(col_name, 2, fin100_project.fin_id.fin_no, border2)
                        sheet.write(col_name, 3, fin100_project.projects_residual, border2)
                        sheet.write(col_name, 4, fin100_project.projects_reserve, border2)
                        sheet.write(col_name, 5, fin100_project.projects_return, border2)
                        sheet.write(col_name, 6, fin100_project.projects_residual_amount, border2)
                        sheet.write(col_name, 7, fin100_project.fin100_state, border2)
                        col_name += 1

                    sheet.write(col_name, 1, '',)
                    sheet.write(col_name, 2, '', )
                    sheet.write(col_name, 3, 'Total', border)
                    sheet.write(col_name, 4, sum_reserve, border)
                    sheet.write(col_name, 5, sum_return, border)
                    sheet.write(col_name, 6, sum_residual_amount, border)
                    sheet.write(col_name, 7, '',)
                    col_name += 2
            count_aa += 1

