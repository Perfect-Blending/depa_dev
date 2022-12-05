# _*_ coding: utf-8
from odoo import models, fields, api,_

from datetime import datetime
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}

class ins_advances_xlsx(models.AbstractModel):
    _name = 'report.dynamic_xlsx.ins_advances_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            #'border': True
        })
        self.format_merged_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'right': True,
            'left': True,
            'font': 'Arial',
        })
        self.format_merged_header_without_border = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        self.content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'font': 'Arial',
        })
        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        self.line_header_total = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        self.line_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })
        self.line_header_left_total = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        self.line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        self.line_header_light_total = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        self.line_header_light_left = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })
        self.line_header_highlight = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        self.line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })

    def prepare_report_filters(self, data, filter):
        """It is writing under second page"""
        self.row_pos_2 += 2
        if filter:
            date = filter.get('date_from','')
            if date:
                # Date from
                self.sheet_2.write_string(self.row_pos_2, 0, _('Date from'),
                                        self.format_header)
                self.sheet_2.write_datetime(self.row_pos_2, 1, self.convert_to_date(str(filter['date_from']) or ''),
                                        self.line_header_light_date)
                self.row_pos_2 += 1
                self.sheet_2.write_string(self.row_pos_2, 0, _('Date to'),
                                        self.format_header)
                self.sheet_2.write_datetime(self.row_pos_2, 1, self.convert_to_date(str(filter['date_to']) or ''),
                                        self.line_header_light_date)



    def prepare_report_contents(self, acc_lines, line_total, filter):
        # self.row_pos += 1
        # self.sheet.merge_range(self.row_pos, 0, self.row_pos, 20, ' วงเงินสดย่อย : ' + filter.get('fund'), self.format_merged_header)

        if filter.get('date_from'):
            self.row_pos += 1
            # self.sheet.merge_range(self.row_pos, 1, self.row_pos, 3, 'Initial Balance', self.format_merged_header)
            self.sheet.write_datetime(self.row_pos, 4, self.convert_to_date(filter.get('date_from')),
                                      self.format_merged_header_without_border)
            self.sheet.write_string(self.row_pos, 5, _(' To '),
                                      self.format_merged_header_without_border)
            self.sheet.write_datetime(self.row_pos, 6, self.convert_to_date(filter.get('date_to')),
                                      self.format_merged_header_without_border)

        # self.sheet.merge_range(self.row_pos, 7, self.row_pos, 9, 'Ending Balance', self.format_merged_header)

        self.row_pos += 1

        self.sheet.write_string(self.row_pos, 0, _('เลขที่สัญญา FIN 401'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 1, _('วันที่อนุมัติ'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 2, _('ชื่อผู้ยืม'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 3, _('ฝ่าย/ส่วนงาน'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 4, _('จำนวนเงินยืมทดรอง'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 5, _('วันที่จ่าย'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 6, _('วันที่เริ่มต้น'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 7, _('วันที่สิ้นสุดยืม'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 8, _('วันครบกำหนด'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 9, _('จำนวนวันเกินกำหนด'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 10, _('วันที่รับเอกสาร'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 11, _('วันที่รับเงิน'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 12, _('ค่าใช้จ่ายจริง'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 13, _('วันที่อนุมัติหักล้างเงินยืมทดลอง'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 14, _('หมายเหตุ'),
                                self.format_header)

        if acc_lines:
            for line in acc_lines:  # Normal lines
                self.row_pos += 1
                self.sheet.write_string(self.row_pos, 0, line.get('name'), self.line_header_light)
                self.sheet.write_string(self.row_pos, 1, line.get('due_date') or '', self.line_header_light)
                self.sheet.write_string(self.row_pos, 2, line.get('employee') or '', self.line_header_light)
                self.sheet.write_string(self.row_pos, 3, line.get('department') or '', self.line_header_light)
                self.sheet.write_number(self.row_pos, 4, float(line.get('contract_amount')),
                                        self.line_header_light)

                self.sheet.write_string(self.row_pos, 5, line.get('date'), self.line_header_light)
                self.sheet.write_string(self.row_pos, 6, line.get('date') or '', self.line_header_light)
                self.sheet.write_string(self.row_pos, 7, line.get('contract_end') or '', self.line_header_light)
                self.sheet.write_string(self.row_pos, 8, line.get('contract_end') or '', self.line_header_light)
                self.sheet.write_string(self.row_pos, 9, line.get('doc_date'), self.line_header_light)
                self.sheet.write_string(self.row_pos, 10, line.get('fin_date201'), self.line_header_light)
                self.sheet.write_string(self.row_pos, 11, line.get('fin_date201') or '', self.line_header_light)
                self.sheet.write_number(self.row_pos, 12, float(line.get('amount_clear')), self.line_header_light)
                self.sheet.write_string(self.row_pos, 13, line.get('action_date201') or '', self.line_header_light)
                self.sheet.write_string(self.row_pos, 14, line.get('fin_remark201') or '', self.line_header_light)

            # Sub total line
            self.row_pos += 2
            self.sheet.merge_range(self.row_pos, 0, self.row_pos, 3, 'รวม', self.format_title)
            self.sheet.write_number(self.row_pos,4, float(line_total.get('total_contract_amount')), self.line_header_highlight)


    def _format_float_and_dates(self, currency_id, lang_id):

        self.line_header.num_format = currency_id.excel_format

        self.line_header_light.num_format = currency_id.excel_format

        self.line_header_highlight.num_format = currency_id.excel_format

        self.line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        self.format_merged_header_without_border.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

    def convert_to_date(self, datestring=False):
        if datestring:
            datestring = fields.Date.from_string(datestring).strftime(self.language_id.date_format)
            return datetime.strptime(datestring, self.language_id.date_format)
        else:
            return False

    def generate_xlsx_report(self, workbook, data, record):
        self._define_formats(workbook)
        self.row_pos = 0
        self.row_pos_2 = 0
        self.sheet = workbook.add_worksheet('Advances')
        self.sheet_2 = workbook.add_worksheet('Filters')
        self.sheet.set_column(0, 0, 30)
        self.sheet.set_column(1, 1, 15)
        self.sheet.set_column(2, 2, 15)
        self.sheet.set_column(3, 3, 15)
        self.sheet.set_column(4, 4, 15)
        self.sheet.set_column(5, 5, 15)
        self.sheet.set_column(6, 6, 15)
        self.sheet.set_column(7, 7, 15)
        self.sheet.set_column(8, 8, 15)
        self.sheet.set_column(9, 9, 15)

        self.sheet_2.set_column(0, 0, 35)
        self.sheet_2.set_column(1, 1, 25)
        self.sheet_2.set_column(2, 2, 25)
        self.sheet_2.set_column(3, 3, 25)
        self.sheet_2.set_column(4, 4, 25)
        self.sheet_2.set_column(5, 5, 25)
        self.sheet_2.set_column(6, 6, 25)

        self.sheet.freeze_panes(3, 0)

        self.sheet.set_zoom(80)

        self.sheet.screen_gridlines = False
        self.sheet_2.screen_gridlines = False
        self.sheet_2.protect()

        # For Formating purpose
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            data = record.read()
            self.sheet.merge_range(0, 0, 0, 18, 'ทะเบียนคุมลูกหนี้เงินยืมทดรองจ่าย', self.format_title)

            self.dateformat = self.env.user.lang
            filters, account_lines, line_total = record.get_report_datas()

            # # Filter section
            self.prepare_report_filters(data, filters)
            # # Content section
            self.prepare_report_contents(account_lines,line_total, filters)
