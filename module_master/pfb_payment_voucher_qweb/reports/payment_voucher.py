from odoo import api, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class PaymentVoucherForm(models.AbstractModel):
    _name = 'report.pfb_payment_voucher_qweb.payment_voucher_pdf_report_pdf'

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
        cheque_number = ''
        cheque_date = ''
        cheque_bank = ''
        cheque_amount = 0

        i = 0
        doc_data = {}
        for doc in docs:
            doc_data[i] = {}
            doc_data[i]['current_date'] = self._convert_date_to_bhuddhist(datetime.now() + timedelta(hours=7))
            doc_data[i]['narration'] = doc.narration
            doc_data[i]['sum_credit'] = 0
            doc_data[i]['sum_debit'] = 0
            doc_data[i]['line_ids'] = {}
            line_ids_obj = self.env['account.move.line'].search([
                ('move_id', '=', doc.id)
            ], order='debit desc')
            for line in line_ids_obj:
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

            print_date = self._convert_date_to_bhuddhist(datetime.now())
            for line in doc.line_ids:

                cheque_no_payment = line.payment_id.cheque_no.cheque_number
                obj = self.env['account.cheque'].search([
                    ('cheque_number', '=', cheque_no_payment),
                ])
                cheque_name = obj.cheque_number
                print(cheque_no_payment, obj)
                if cheque_name == cheque_no_payment and cheque_name != False:
                    cheque_number = obj.cheque_number
                    cheque_bank = obj.journal_id.bank_id.name + (obj.journal_id.bank_id.branch_bank
                                                                 and (' - ' + obj.journal_id.bank_id.branch_bank) or '')
                    cheque_amount = obj.amount
                    if not cheque_name:
                        cheque_date = ''
                    else:
                        cheque_date = self._convert_date_to_bhuddhist2(obj.cheque_date)
                else:
                    {}

                date_wt = []
                name_wt = []
                base_wt = []
                amount_wt = []
                payment_wt = []
                number_inv = []
                name_inv = []
                amount_inv = []
                date_inv = []
                partner_tax = []
                sum_inv = 0
                sum_amount_wt = 0
                number_wt = []
                sequence_wt = []
                for inv in line[0].payment_id.reconciled_invoice_ids:
                    number_inv.append(inv.number)
                    name_inv.append(inv.name)
                    amount_inv.append(inv.amount_total)
                    date_inv.append(inv.date_invoice)
                    partner_tax.append(inv.partner_id.vat)

                for sum_inv_ids in amount_inv:
                    sum_inv += sum_inv_ids

                for wt in line[0].payment_id.wt_cert_ids:
                    date_wt.append(wt.date)
                    name_wt.append(wt.wt_line.wt_cert_income_desc)
                    base_wt.append(wt.wt_line.base)
                    amount_wt.append(wt.wt_line.amount)
                    payment_wt.append(wt.payment_id.name)
                    number_wt.append(wt.number_wt)

                for i in amount_wt:
                    sum_amount_wt += i

            return {
                'doc_ids': docs.ids,
                'doc_model': 'account.move',
                'doc_data': doc_data,
                'docs': docs,
                'date_wt': date_wt,
                'name_wt': name_wt,
                'base_wt': base_wt,
                'amount_wt': amount_wt,
                'payment_wt': payment_wt,
                'sum_amount_wt': sum_amount_wt,
                'cheque_no_payment': cheque_no_payment,
                'cheque_number': cheque_number,
                'cheque_date': cheque_date,
                'cheque_bank': cheque_bank,
                'cheque_amount': cheque_amount,
                'print_date': print_date,
                'number_inv': number_inv,
                'name_inv': name_inv,
                'amount_inv': amount_inv,
                'sum_inv': sum_inv,
                'date_inv': date_inv,
                'partner_tax': partner_tax,
                'number_wt': number_wt,
            }
