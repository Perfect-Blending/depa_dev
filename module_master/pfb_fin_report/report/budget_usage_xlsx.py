import logging
from odoo import models

_logger = logging.getLogger(__name__)


class ReportBudgetUsageReportXlsx(models.AbstractModel):
    _name = 'report.pfb_fin_report.report_budget_usage_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        # self._define_formats(workbook)
        sheet = workbook.add_worksheet('รายงานการใช้งบประมาณ')
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
        header = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })

        sheet.merge_range('B2:Q3', 'รายงานการใช้งบประมาณ', header)
        sheet.set_column('A:P', 15, )
        sheet.set_row(3, 20, )
        sheet.write(3, 1, 'No', border)
        sheet.write(3, 2, 'FIN type', border)
        sheet.write(3, 3, 'สินค้า', border)
        sheet.write(3, 4, 'งบประมาณ', border)
        sheet.write(3, 5, 'Unit price', border)
        sheet.write(3, 6, 'Quantity', border)
        sheet.write(3, 7, 'Subtotal', border)
        sheet.write(3, 8, 'Fin100 line residual', border)
        sheet.write(3, 9, 'FIN401 current amount', border)
        sheet.write(3, 10, 'Lend total', border)
        sheet.write(3, 11, 'Fin100 line residual', border)
        sheet.write(3, 12, 'State', border)
        sheet.write(3, 13, 'FIN201 current amount', border)
        sheet.write(3, 14, 'Payment amount', border)
        sheet.write(3, 15, 'Fin100 line residual', border)
        sheet.write(3, 16, 'State', border)

        row = 4
        col = 1
        for results in objects.results:
            for fin100 in results.fin_lines_to_edit:
                if len(fin100.fin201_line_ids) > 0 and len(fin100.fin401_line_ids) == 0:
                    line_num = 0
                    group_201 = []
                    fin_no = ''
                    for fin201 in fin100.fin201_line_ids:
                        group_201.append(fin201)
                    for cc in group_201:
                        if fin_no != fin100.fin_id.fin_no:
                            sheet.write(row, 1, fin100.fin_id.fin_no, border2)
                            sheet.write(row, 2, fin100.fin_id.fin_type, border2)
                            sheet.write(row, 3, fin100.product_id.name, border2)
                            sheet.write(row, 4, fin100.projects_and_plan.name, border2)
                            sheet.write(row, 5, fin100.price_unit, border2)
                            sheet.write(row, 6, fin100.product_uom_qty, border2)
                            sheet.write(row, 7, fin100.price_subtotal, border2)
                            sheet.write(row, 8, fin100.balance, border2)
                        else:
                            sheet.write(row, 1, '', border2)
                            sheet.write(row, 2, '', border2)
                            sheet.write(row, 3, '', border2)
                            sheet.write(row, 4, '', border2)
                            sheet.write(row, 5, '', border2)
                            sheet.write(row, 6, '', border2)
                            sheet.write(row, 7, '', border2)
                            sheet.write(row, 8, '', border2)
                        sheet.write(row, 9, '', border2)
                        sheet.write(row, 10, '', border2)
                        sheet.write(row, 11, '', border2)
                        sheet.write(row, 12, '', border2)
                        for fin201_line in group_201[line_num]:
                            print(fin201_line)
                            sheet.write(row, 13, fin201_line.fin201_current_amount, border2)
                            sheet.write(row, 14, fin201_line.payment_amount, border2)
                            sheet.write(row, 15, fin201_line.fin100_line_residual_amount, border2)
                            sheet.write(row, 16, fin201_line.fin201_state, border2)
                        fin_no = fin100.fin_id.fin_no
                        line_num += 1
                        row += 1
                if len(fin100.fin401_line_ids) > 0 and len(fin100.fin201_line_ids) == 0:
                    fin_no = ''
                    for fin401 in fin100.fin401_line_ids:
                        if fin_no != fin100.fin_id.fin_no:
                            sheet.write(row, 1, fin100.fin_id.fin_no, border2)
                            sheet.write(row, 2, fin100.fin_id.fin_type, border2)
                            sheet.write(row, 3, fin100.product_id.name, border2)
                            sheet.write(row, 4, fin100.projects_and_plan.name, border2)
                            sheet.write(row, 5, fin100.price_unit, border2)
                            sheet.write(row, 6, fin100.product_uom_qty, border2)
                            sheet.write(row, 7, fin100.price_subtotal, border2)
                            sheet.write(row, 8, fin100.balance, border2)
                        else:
                            sheet.write(row, 1, '', border2)
                            sheet.write(row, 2, '', border2)
                            sheet.write(row, 3, '', border2)
                            sheet.write(row, 4, '', border2)
                            sheet.write(row, 5, '', border2)
                            sheet.write(row, 6, '', border2)
                            sheet.write(row, 7, '', border2)
                            sheet.write(row, 8, '', border2)
                        sheet.write(row, 9, fin401.fin401_current_amount, border2)
                        sheet.write(row, 10, fin401.lend, border2)
                        sheet.write(row, 11, fin401.fin100_line_residual_amount, border2)
                        sheet.write(row, 12, fin401.fin401_state, border2)

                        sheet.write(row, 13, '', border2)
                        sheet.write(row, 14, '', border2)
                        sheet.write(row, 15, '', border2)
                        sheet.write(row, 16, '', border2)

                        fin_no = fin100.fin_id.fin_no
                        row += 1
                if len(fin100.fin401_line_ids) > 0 and len(fin100.fin201_line_ids) > 0:
                    line_num = 0
                    count_fin201 = 0
                    group_201 = []
                    fin_no = ''
                    for fin201 in fin100.fin201_line_ids:
                        group_201.append(fin201)
                    for fin401 in fin100.fin401_line_ids:
                        if fin_no != fin100.fin_id.fin_no:
                            sheet.write(row, 1, fin100.fin_id.fin_no, border2)
                            sheet.write(row, 2, fin100.fin_id.fin_type, border2)
                            sheet.write(row, 3, fin100.product_id.name, border2)
                            sheet.write(row, 4, fin100.projects_and_plan.name, border2)
                            sheet.write(row, 5, fin100.price_unit, border2)
                            sheet.write(row, 6, fin100.product_uom_qty, border2)
                            sheet.write(row, 7, fin100.price_subtotal, border2)
                            sheet.write(row, 8, fin100.balance, border2)
                        else:
                            sheet.write(row, 1, '', border2)
                            sheet.write(row, 2, '', border2)
                            sheet.write(row, 3, '', border2)
                            sheet.write(row, 4, '', border2)
                            sheet.write(row, 5, '', border2)
                            sheet.write(row, 6, '', border2)
                            sheet.write(row, 7, '', border2)
                            sheet.write(row, 8, '', border2)
                        sheet.write(row, 9, fin401.fin401_current_amount, border2)
                        sheet.write(row, 10, fin401.lend, border2)
                        sheet.write(row, 11, fin401.fin100_line_residual_amount, border2)
                        sheet.write(row, 12, fin401.fin401_state, border2)

                        for fin201_line in group_201[line_num]:
                            print(fin201_line)
                            sheet.write(row, 13, fin201_line.fin201_current_amount, border2)
                            sheet.write(row, 14, fin201_line.payment_amount, border2)
                            sheet.write(row, 15, fin201_line.fin100_line_residual_amount, border2)
                            sheet.write(row, 16, fin201_line.fin201_state, border2)
                        fin_no = fin100.fin_id.fin_no
                        line_num += 1
                        row += 1
                    count_fin201 = len(group_201) - line_num
                    if count_fin201 != 0:
                        for loop in range(count_fin201):
                            if fin_no != fin100.fin_id.fin_no:
                                sheet.write(row, 1, fin100.fin_id.fin_no, border2)
                                sheet.write(row, 2, fin100.fin_id.fin_type, border2)
                                sheet.write(row, 3, fin100.product_id.name, border2)
                                sheet.write(row, 4, fin100.projects_and_plan.name, border2)
                                sheet.write(row, 5, fin100.price_unit, border2)
                                sheet.write(row, 6, fin100.product_uom_qty, border2)
                                sheet.write(row, 7, fin100.price_subtotal, border2)
                                sheet.write(row, 8, fin100.balance, border2)
                            else:
                                sheet.write(row, 1, '', border2)
                                sheet.write(row, 2, '', border2)
                                sheet.write(row, 3, '', border2)
                                sheet.write(row, 4, '', border2)
                                sheet.write(row, 5, '', border2)
                                sheet.write(row, 6, '', border2)
                                sheet.write(row, 7, '', border2)
                                sheet.write(row, 8, '', border2)
                            sheet.write(row, 9, '', border2)
                            sheet.write(row, 10, '', border2)
                            sheet.write(row, 11, '', border2)
                            sheet.write(row, 12, '', border2)

                            for fin201_line in group_201[line_num]:
                                print(fin201_line)
                                sheet.write(row, 13, fin201_line.fin201_current_amount, border2)
                                sheet.write(row, 14, fin201_line.payment_amount, border2)
                                sheet.write(row, 15, fin201_line.fin100_line_residual_amount, border2)
                                sheet.write(row, 16, fin201_line.fin201_state, border2)
                            fin_no = fin100.fin_id.fin_no
                            line_num += 1
                            row += 1
                if len(fin100.fin401_line_ids) == 0 and len(fin100.fin201_line_ids) == 0:
                    fin_no = ''
                    if fin_no != fin100.fin_id.fin_no:
                        sheet.write(row, 1, fin100.fin_id.fin_no, border2)
                        sheet.write(row, 2, fin100.fin_id.fin_type, border2)
                        sheet.write(row, 3, fin100.product_id.name, border2)
                        sheet.write(row, 4, fin100.projects_and_plan.name, border2)
                        sheet.write(row, 5, fin100.price_unit, border2)
                        sheet.write(row, 6, fin100.product_uom_qty, border2)
                        sheet.write(row, 7, fin100.price_subtotal, border2)
                        sheet.write(row, 8, fin100.balance, border2)
                    else:
                        sheet.write(row, 1, '', border2)
                        sheet.write(row, 2, '', border2)
                        sheet.write(row, 3, '', border2)
                        sheet.write(row, 4, '', border2)
                        sheet.write(row, 5, '', border2)
                        sheet.write(row, 6, '', border2)
                        sheet.write(row, 7, '', border2)
                        sheet.write(row, 8, '', border2)
                    sheet.write(row, 9, '', border2)
                    sheet.write(row, 10, '', border2)
                    sheet.write(row, 11, '', border2)
                    sheet.write(row, 12, '', border2)

                    sheet.write(row, 13, '', border2)
                    sheet.write(row, 14, '', border2)
                    sheet.write(row, 15, '', border2)
                    sheet.write(row, 16, '', border2)

                    fin_no = fin100.fin_id.fin_no
                    row += 1
