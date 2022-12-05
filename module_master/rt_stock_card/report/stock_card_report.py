from odoo import api, models
from odoo.tools import float_round

class report_stock_card(models.AbstractModel):
    _name = 'report.stock_card.report_stockcard_report'
    _description = "Stock Card Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        products = self.env['product.template'].browse(data['form']['ids'])
        return {
            'doc_ids': data.get('ids',[]),
            'doc_model': 'product.template',
            'docs': products,
            'data': dict(
                data,
            ),
        }

class report_stock_card_summary(models.AbstractModel):
    _name = 'report.stock_card.report_stockcard_summary_report'
    _description = "Stock Card Summary Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        products = self.env['product.template'].browse(data['form']['ids'])
        return {
            'doc_ids': docids,
            'doc_model': 'stock.card',
            'docs': self.env['stock.card'].browse(self.env.context.get('active_ids')),
            'data': dict(
                data,
            ),
        }
