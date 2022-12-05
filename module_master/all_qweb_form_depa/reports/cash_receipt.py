from odoo import api, models
from bahttext import bahttext
from dateutil.relativedelta import relativedelta


class CashReceiptForm(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.cash_receipt_pdf_report_pdf'


    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.customer.receipts'].browse(docids)
        thaibahttext = ''
        sum_total = 0
        sum_tt = 0
        check_if = 0
        group = []
        for doc in docs:
            if doc.amount_cash != 0:
                check_if = 1
            elif doc.cheque_ids:
                check_if = 2
            elif doc.banktr_ids:
                check_if = 3
            else:
                check_if = 0
            print(check_if)
            for line in doc.line_ids:
                group.append(line)
                sum_total += line.amount_receipt
        sum_tt = sum_total
        thaibahttext = bahttext(sum_total)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'bione.customer.receipts',
            'docs': docs,
            'thaibahttext': thaibahttext,
            'check_if': check_if,
            'group': group,
        }


class CashPaymentForm(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.cash_payment_pdf_report_pdf'


    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.supplier.payment'].browse(docids)
        thaibahttext = ''
        sum_total = 0
        sum_tt = 0
        check_if = 0
        for doc in docs:
            if doc.amount_cash != 0:
                check_if = 1
            elif doc.cheque_ids:
                check_if = 2
            elif doc.banktr_ids:
                check_if = 3
            else:
                check_if = 0
            print(check_if)
            for line in doc.other_ids:
                sum_total += line.amount
        sum_tt = sum_total
        thaibahttext = bahttext(sum_total)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'bione.supplier.payment',
            'docs': docs,
            'thaibahttext': thaibahttext,
            'check_if': check_if,
        }


class AccountAdvanceForm(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.account_advance_report_pdf'


    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.advance.clear'].browse(docids)
        thaibahttext = ''
        check_if = 0
        sum_amount = 0
        bank_cash = ''
        for doc in docs:
            for line in doc.lines:
                sum_amount += line.amount
                bank_cash = line.account_id.user_type_id.name
        if bank_cash == 'Bank and Cash':
            check_if = 3
        else:
            check_if = 1

        thaibahttext = bahttext(sum_amount)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.advance.clear',
            'docs': docs,
            'thaibahttext': thaibahttext,
            'check_if': check_if,
        }
