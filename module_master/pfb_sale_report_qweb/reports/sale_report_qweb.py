from odoo import api, models
from dateutil.relativedelta import relativedelta


class PfbSaleReport(models.AbstractModel):
    _name = 'report.pfb_sale_report_qweb.sale_report_pdf'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    def month_convert(self, convert_month):
        str_month = str(convert_month)[5:7]
        month = ''
        if str_month == '01':
            month = 'มกราคม'
        if str_month == '02':
            month = 'กุมภาพันธ์'
        if str_month == '03':
            month = 'มีนาคม'
        if str_month == '04':
            month = 'เมษายน'
        if str_month == '05':
            month = 'พฤษภาคม'
        if str_month == '06':
            month = 'มิถุนายน'
        if str_month == '07':
            month = 'กรกฎาคม'
        if str_month == '08':
            month = 'สิงหาคม'
        if str_month == '09':
            month = 'กันยายน'
        if str_month == '10':
            month = 'ตุลาคม'
        if str_month == '11':
            month = 'พฤศจิกายน'
        if str_month == '12':
            month = 'ธันวาคม'
        return month

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['pfb.sale.order.tree'].browse(docids)
        count = 0
        date_group = []
        len_date = 0
        print(docs)
        for doc in docs:
            date_group.append(doc.date_dat)
            len_date += 1
        print(len_date)
        mount_one = self.month_convert(date_group[0])
        mount_two = self.month_convert(date_group[-1])
        print(mount_one,mount_two)

        #     income_tax_form = doc.pnd
        #     company = doc.company_id.name
        #     count += len(doc)
        print(docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'pfb.sale.order.tree',
            'docs': docs,
            'mount_one': mount_one,
            'mount_two': mount_two,
            # 'income_tax_form': income_tax_form,
            # 'company': company,
        }
