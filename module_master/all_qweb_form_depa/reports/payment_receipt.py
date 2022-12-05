from odoo import api, models
from bahttext import bahttext
from dateutil.relativedelta import relativedelta
from num2words import num2words


class PaymentReceiptForm(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.payment_receipt_pdf_report_pdf2'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.customer.receipts'].browse(docids)

        thaibahttext = ''
        sum_untaxed3 = 0
        sum_vat2 = 0
        sum_total = 0
        check_if = 0
        for doc in docs:

            count1 = 0
            sum_text = 0.00
            count2 = []
            description = []
            unit_price = []
            qty = []
            sub_total = []
            sum_price = 0
            if doc.amount_cash != 0:
                check_if = 1
            elif doc.cheque_ids:
                check_if = 2
            elif doc.banktr_ids:
                check_if = 3
            else:
                check_if = 0
            sum_untaxed = 0
            sum_vat = 0
            sum_qty = 0
            unit_qty = 0
            if doc.vat_ids:
                for line_vat in doc.vat_ids:
                    sum_untaxed += line_vat.amount_untaxed
                    sum_vat += line_vat.amount_tax
                for line_inv in doc.line_ids:
                    sum_qty += line_inv.quantity
            for line in doc.line_ids:
                count1 += 1
                sum_price += line.amount_receipt
                count2.append(count1)
                description.append(line.name)
                qty.append(line.quantity)
                unit_qty = sum_qty / sum_untaxed
                if line.amount_receipt == line.amount_total:
                    unit_price.append(line.price_unit)
                    sub_total.append(line.amount_receipt)
                    sum_text = sum_price + doc.amount_vat
                else:
                    unit_price.append(unit_qty)
                    sub_total.append(unit_qty * line.quantity)
                    sum_text = sum_untaxed + sum_vat
            thaibahttext = bahttext(sum_text)

            return {
                'doc_ids': docs.ids,
                'doc_model': 'bione.customer.receipts',
                'docs': docs,
                'thaibahttext': thaibahttext,
                'count2': count2,
                'description': description,
                'unit_price': unit_price,
                'qty': qty,
                'sub_total': sub_total,
                'sum_price': sum_price,
                'check_if': check_if,
                # 'vat': vat,
                # 'sum_amount': sum_amount,
            }


class PaymentReceiptForm2(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.payment_receipt_pdf_report_pdf3'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.customer.payment'].browse(docids)
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
            print()
            group_inv = []
            for line_ids in doc.line_ids:
                group_inv.append(line_ids)

            return {
                'doc_ids': docs.ids,
                'doc_model': 'bione.customer.payment',
                'docs': docs,
                'check_if': check_if,
                'group_inv': group_inv,
            }


class PaymentReceiptForm4(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.payment_receipt_pdf_report_pdf4'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.customer.payment'].browse(docids)
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
            print()
            group_inv = []
            for line_ids in doc.line_ids:
                group_inv.append(line_ids)

            return {
                'doc_ids': docs.ids,
                'doc_model': 'bione.customer.payment',
                'docs': docs,
                'check_if': check_if,
                'group_inv': group_inv,
            }


class ReportCustomerReceipts(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.report_customer_receipts'
    _description = 'Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.customer.receipts'].browse(docids)

        return {
            'doc_ids': self._ids,
            'doc_model': 'bione.customer.receipts',
            'docs': docs,
            'data': data,

        }


class CustomerPayment(models.Model):
    _inherit = 'bione.customer.payment'

    @api.multi
    def bath_text(self, amount):
        return bahttext(amount)


class CustomerReceipts(models.Model):
    _inherit = 'bione.customer.receipts'

    @api.multi
    def bath_text(self, amount):
        return bahttext(amount)
