from odoo import api, models
from datetime import datetime , timedelta
from dateutil.relativedelta import relativedelta


class PurchaseVoucherForm(models.AbstractModel):
    _name = 'report.pfb_purchase_voucher_qweb.purchase_voucher_pdf_report_pdf'

    def _convert_date_to_bhuddhist(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y %H:%M:%S')
        return date_converted

    def _convert_date_to_bhuddhist2(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        i = 0
        doc_data = {}
        for doc in docs:
            doc_data[i] = {}
            doc_data[i]['date'] = self._convert_date_to_bhuddhist2(doc.date)
            doc_data[i]['current_date'] = self._convert_date_to_bhuddhist(datetime.now() + timedelta(hours=7) )
            doc_data[i]['name'] = doc.name
            doc_data[i]['ref'] = doc.ref
            doc_data[i]['narration'] = doc.narration
            doc_data[i]['sum_credit'] = 0
            doc_data[i]['sum_debit'] = 0
            doc_data[i]['line_ids'] = {}
            doc_data[i]['inv'] = {}
            line_ids_obj = self.env['account.move.line'].search([
                ('move_id', '=', doc.id)
            ], order='debit desc')
            for line in line_ids_obj:
                doc_data[i]['partner_sale'] = line[0].partner_id.name
                doc_data[i]['inv_number'] = line[0].invoice_id.number

                if line.account_id.code in doc_data[i]['line_ids']:
                    doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                    doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                else:
                    doc_data[i]['line_ids'][line.account_id.code] = {
                        'account_code': line.account_id.code,
                        'name': line.account_id.name,
                        'analytic_account': line.analytic_account_id.code,
                        'debit': line.debit,
                        'credit': line.credit
                    }
                doc_data[i]['sum_debit'] += line.debit
                doc_data[i]['sum_credit'] += line.credit

            i += 1
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'doc_data': doc_data,
            'docs': docs,
        }
