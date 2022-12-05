from odoo import api, models
from bahttext import bahttext


class ParticularReport(models.AbstractModel):
    _name = 'report.pfb_custom_qweb_report.purchase_order_report_view'

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        thaibahttext = ''
        for doc in docs:
            thaibahttext = bahttext(doc.amount_total)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'thaibahttext': thaibahttext,
        }