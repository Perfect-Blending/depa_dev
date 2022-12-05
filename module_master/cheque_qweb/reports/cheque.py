from odoo import api, models
from bahttext import bahttext


class ChequeForm(models.AbstractModel):
    _name = 'report.cheque_qweb.cheque_pdf_report_pdf'

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.cheque'].browse(docids)
        thaibahttext = ''
        for doc in docs:
            thaibahttext = bahttext(doc.amount)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'bione.cheque',
            'docs': docs,
            'thaibahttext': thaibahttext,
        }