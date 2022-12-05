from odoo import api, models
from bahttext import bahttext
from dateutil.relativedelta import relativedelta


class CheckWorkForm(models.AbstractModel):
    _name = 'report.check_work_qweb.check_work_pdf_report_pdf'

    def _convert_date_to_bhuddhist(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['work.acceptance'].browse(docids)
        thaibahttext = ''
        number_po = ''
        analytic = ''
        wa_name = ''
        wa_date = ''
        wa_date2 = ''
        amount_untaxed = 0
        amount_tax = 0
        amount_total = 0
        check_date = ''
        bo_name = ''
        bo_pn = ''
        bo_ad = ''
        bo_pn = ''
        bo_od = ''
        bo_dd = ''
        wa_count = ''
        for doc in docs:
            if doc.check_date:
                check_date = self._convert_date_to_bhuddhist(doc.check_date)
            # print(check_date, 1)
            fines = doc.fines
            date_check = doc.date_check
            notes_check = doc.notes_check

            number_po = doc.purchase_id.name
            analytic = doc.purchase_id.project_id.code
            wa_name = doc.name
            wa_count = doc.purchase_id.invoice_count
            wa_date = self._convert_date_to_bhuddhist(doc.date_receive)
            wa_date2 = self._convert_date_to_bhuddhist(doc.date_accept)
            bo_name = doc.purchase_id.requisition_id.contract_number
            bo_pn = doc.purchase_id.requisition_id.vendor_id.name
            if doc.purchase_id.requisition_id:
                bo_ad = self._convert_date_to_bhuddhist(doc.purchase_id.requisition_id.date_end)
                bo_od = self._convert_date_to_bhuddhist(doc.purchase_id.requisition_id.ordering_date)
                bo_dd = self._convert_date_to_bhuddhist(doc.purchase_id.requisition_id.schedule_date)
            amount_untaxed = doc.purchase_id.amount_untaxed
            amount_tax = doc.purchase_id.amount_tax
            amount_total = doc.purchase_id.amount_total

            count = 0
            count2 = []
            product_name = []
            product_qty = []
            product_uom = []
            price_unit = []
            price_total = []
            number_km = doc.invoice_ref
            instalment = doc.instalment_wa
            date_km = ''
            employee = []
            position = []
            count_employee = 0
            sum_wa = 0
            for inv in doc.purchase_id.invoice_ids:
                date_km = inv.date_due
            for line in doc.wa_line_ids:
                count += 1
                count2.append(count)
                product_name.append(line.name)
                product_qty.append(line.product_qty)
                product_uom.append(line.product_uom.name)
                price_unit.append(line.price_unit)
                price_total.append(line.price_subtotal)
                sum_wa += line.price_subtotal
            if doc.purchase_id:
                for line_agreement in doc.purchase_id.requisition_id.line_agreement:
                    employee.append(line_agreement.test_one.name)
                    position.append(line_agreement.test_two.jop_work)
                    count_employee = len(employee)
            else:
                for line_agreement in doc.purchase_id.requisition_id.line_agreement:
                    employee.append(line_agreement.test_one.name)
                    position.append(line_agreement.test_two.jop_work)
                    count_employee = len(employee)

            thaibahttext = bahttext(sum_wa)
            print(employee, count_employee)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'work.acceptance',
            'docs': docs,
            'thaibahttext': thaibahttext,
            'number_po': number_po,
            'amount_untaxed': amount_untaxed,
            'amount_tax': amount_tax,
            'amount_total': amount_total,
            'product_name': product_name,
            'product_qty': product_qty,
            'price_unit': price_unit,
            'price_total': price_total,
            'analytic': analytic,
            'count2': count2,
            'wa_name': wa_name,
            'wa_date': wa_date,
            'wa_date2': wa_date2,
            'number_km': number_km,
            'date_km': date_km,
            'bo_name': bo_name,
            'bo_pn': bo_pn,
            'bo_ad': bo_ad,
            'bo_od': bo_od,
            'bo_dd': bo_dd,
            'wa_count': wa_count,
            'instalment': instalment,
            'employee': employee,
            'position': position,
            'count_employee': count_employee,
            'check_date': check_date,
            'fines': fines,
            'notes_check': notes_check,
            'date_check': date_check,

        }
