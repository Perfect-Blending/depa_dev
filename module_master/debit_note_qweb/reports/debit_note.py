from odoo import api, models
from bahttext import bahttext


class DebitNoteForm(models.AbstractModel):
    _name = 'report.debit_note_qweb.debit_note_pdf_report_pdf'

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.invoice'].browse(docids)
        thaibahttext = ''
        reference = ''
        bank_name = ''
        phone_bank = ''
        for doc in docs:
            reference = doc.name
            if doc.partner_bank_id:
                bank_name = doc.partner_bank_id.partner_id.name
                phone_bank = doc.partner_bank_id.partner_id.mobile
            count = 0
            price_unit_total = 0
            count2 = []
            product_name = []
            price_unit = []
            quantity = []
            uom_name = []
            price_subtotal = []
            thaibahttext = bahttext(doc.amount_total)
            for line in doc.invoice_line_ids:
                price_unit_total = line.price_subtotal / line.quantity
                count += 1
                count2.append(count)
                product_name.append(line.name)
                price_unit.append(price_unit_total)
                quantity.append(line.quantity)
                uom_name.append(line.uom_id.name)
                price_subtotal.append(line.price_subtotal)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.invoice',
            'docs': docs,
            'thaibahttext': thaibahttext,
            'count2': count2,
            'product_name': product_name,
            'price_unit': price_unit,
            'quantity': quantity,
            'uom_name': uom_name,
            'price_subtotal': price_subtotal,
            'reference': reference,
            'bank_name': bank_name,
            'phone_bank': phone_bank,
        }
