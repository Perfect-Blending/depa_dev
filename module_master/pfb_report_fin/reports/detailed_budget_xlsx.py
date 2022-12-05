import logging
from odoo import models

_logger = logging.getLogger(__name__)


class ReportDetailedBudgetReportXlsx(models.AbstractModel):
    _name = 'report.pfb_report_fin.report_detailed_budget_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        for results in objects.results:
            for ws_params in self._get_ws_params(workbook, data, results):
                ws_name = ws_params.get('ws_name')
                ws_name = self._check_ws_name(ws_name)
                ws = workbook.add_worksheet(ws_name)
                generate_ws_method = getattr(
                    self, ws_params['generate_ws_method'])
                generate_ws_method(
                    workbook, ws, ws_params, data, objects, results)


    def _get_ws_params(self, wb, data, results):

        initial_template = {
            '1_ref': {
                'data': {
                    'value': 'Initial',
                    'format': self.format_tcell_center,
                },
                'colspan': 4,
            },
            '2_balance': {
                'data': {
                    'value': '',
                    'format': self.format_tcell_amount_right,
                },
            },
        }
        stock_card_template = {
            '1_date': {
                'header': {
                    'value': 'Date',
                },
                'data': {
                    'value': self._render('self'),
                    'format': self.format_tcell_date_left,
                },
                'width': 25,
            },
            '2_reference': {
                'header': {
                    'value': 'Reference',
                },
                'data': {
                    'value': '',
                    'format': self.format_tcell_left,
                },
                'width': 25,
            },
            '3_input': {
                'header': {
                    'value': 'Input',
                },
                'data': {
                    'value': '',
                },
                'width': 25,
            },
            '4_output': {
                'header': {
                    'value': 'Output',
                },
                'data': {
                    'value': '',
                },
                'width': 25,
            },
            '5_balance': {
                'header': {
                    'value': 'Balance',
                },
                'data': {
                    'value': '',
                },
                'width': 25,
            },
        }

        ws_params = {
            'ws_name': results.name,
            'generate_ws_method': '_stock_card_report',
            'title': '{}'.format(results.name),
            'wanted_list_initial': [k for k in sorted(initial_template.keys())],
            'col_specs_initial': initial_template,
            'wanted_list': [k for k in sorted(stock_card_template.keys())],
            'col_specs': stock_card_template,
        }
        return [ws_params]

    def _stock_card_report(self, wb, ws, ws_params, data, objects, results):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])
        self._set_column_width(ws, ws_params)
        # Title
        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)
        # Filter Table
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_blue_center)
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='data',
            render_space={
                'fiscal_year': objects.fiscal_year or '',
            })
        row_pos += 1
        # Stock Card Table
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_blue_center)
        ws.freeze_panes(row_pos, 0)
        # balance = objects._get_initial(objects.results.filtered(
        #     lambda l: l.product_id == product and l.is_initial))
        # row_pos = self._write_line(
        #     ws, row_pos, ws_params, col_specs_section='data',
        #     render_space={'balance': balance}, col_specs='col_specs_initial',
        #     wanted_list='wanted_list_initial')
        # results_lines = objects.results.filtered(
        #     lambda l: l.product_id == results and not l.is_initial)
        # for line in results_lines:
        #     balance += line.product_in - line.product_out
        #     row_pos = self._write_line(
        #         ws, row_pos, ws_params, col_specs_section='data',
        #         render_space={
        #             'date': line.date or '',
        #             'reference': line.reference or '',
        #             'input': line.product_in or 0,
        #             'output': line.product_out or 0,
        #             'balance': balance,
        #         },
        #         default_format=self.format_tcell_amount_right)
