from odoo import api, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class PurchaseVoucherForm(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.purchase_voucher_pdf_report_pdf'

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
        ii = 1
        len_doc = len(docs)
        doc_data = {}
        for doc in docs:
            print(doc)
            doc_data[i] = {}
            doc_data[i]['date'] = self._convert_date_to_bhuddhist2(doc.date)
            doc_data[i]['current_date'] = self._convert_date_to_bhuddhist(datetime.now() + timedelta(hours=7))
            doc_data[i]['name'] = doc.name
            doc_data[i]['ref'] = doc.ref
            doc_data[i]['narration'] = doc.narration
            doc_data[i]['sum_credit'] = 0
            doc_data[i]['sum_debit'] = 0
            doc_data[i]['partner_sale'] = ''
            doc_data[i]['page'] = 0
            doc_data[i]['line_ids'] = {}
            doc_data[i]['line_inv'] = []
            line_ids_obj = self.env['account.move.line'].search([
                ('move_id', '=', doc.id)
            ], order='debit desc')
            doc_data[i]['analytic_account'] = ''
            for line in line_ids_obj:
                doc_data[i]['partner_sale'] = line[0].partner_id.name
                if line.analytic_account_id.code:
                    if line.account_id.code in doc_data[i]['line_ids']:
                        print('1')
                        if line.analytic_account_id.code in doc_data[i]['line_ids']:
                            print('2')
                            doc_data[i]['line_ids'][line.analytic_account_id.code]['debit'] += line.debit
                            doc_data[i]['line_ids'][line.analytic_account_id.code]['credit'] += line.credit
                        else:
                            print('3')
                            if line.account_id.code in doc_data[i]['line_ids']:
                                print('5')
                                if doc_data[i]['analytic_account'] == line.analytic_account_id.code:
                                    print('51')
                                    doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                                    doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                                else:
                                    print('52')
                                    doc_data[i]['line_ids'][line.analytic_account_id.code] = {
                                        'account_code': line.account_id.code,
                                        'name': line.account_id.name,
                                        'analytic_account': line.analytic_account_id.code,
                                        'debit': line.debit,
                                        'credit': line.credit
                                    }
                            else:
                                print('6')
                                doc_data[i]['line_ids'][line.analytic_account_id.code] = {
                                    'account_code': line.account_id.code,
                                    'name': line.account_id.name,
                                    'analytic_account': line.analytic_account_id.code,
                                    'debit': line.debit,
                                    'credit': line.credit
                                }
                    else:
                        print('7')
                        doc_data[i]['line_ids'][line.account_id.code] = {
                            'account_code': line.account_id.code,
                            'name': line.account_id.name,
                            'analytic_account': line.analytic_account_id.code,
                            'debit': line.debit,
                            'credit': line.credit
                        }
                        doc_data[i]['analytic_account'] = line.analytic_account_id.code
                else:
                    print('8')
                    if line.account_id.code in doc_data[i]['line_ids']:
                        print('9')
                        doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                        doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                    else:
                        print('10')
                        doc_data[i]['line_ids'][line.account_id.code] = {
                            'account_code': line.account_id.code,
                            'name': line.account_id.name,
                            'analytic_account': line.analytic_account_id.code,
                            'debit': line.debit,
                            'credit': line.credit
                        }
                doc_data[i]['sum_debit'] += line.debit
                doc_data[i]['sum_credit'] += line.credit
            print(doc_data[i]['line_ids'])
            doc_data[i]['header'] = 'สำนักงานส่งเสริมเศรษฐกิจดิจิทัล'
            doc_data[i]['header2'] = 'ใบสำคัญรับรู้ค่าใช้จ่าย'
            doc_data[i]['page'] = ii
            for line_inv in doc.line_ids[0].invoice_id.invoice_line_ids:
                doc_data[i]['line_inv'].append(line_inv)
            i += 1
            ii += 1

        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
            'doc_data': doc_data,
            'len_doc': len_doc,
        }
