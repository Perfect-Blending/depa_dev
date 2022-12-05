from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.addons.pfb_sale_report.models.sale_order_tree import generate_bg_report
import uuid


class SaleOrderReportWizard(models.TransientModel):
    _name = 'sale.order.report.wizard'
    _description = 'Sale Order Report Wizard'


    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date Range',
        required=True,
    )
    date_from = fields.Date(
        string='Date From',
    )
    date_to = fields.Date(
        string='Date To',
    )

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.multi
    def button_export_html(self):
        domains = []

        if self.date_from:
            domains.append(('date_from', '=', self.date_from))

        if self.date_to:
            domains.append(('date_to', '=', self.date_to))

        newsession = str(uuid.uuid4())
        print(newsession)
        generate_bg_report(self, newsession, domains)

        title = 'Sale Order Report'
        report_model = 'pfb.sale.order.tree'

        ret = {
            'name': title,
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': report_model,
            'type': 'ir.actions.act_window',
            'domain': [('session', '=', newsession)]
        }

        return ret

    def _prepare_wt_report(self):
        self.ensure_one()
        return {
            'date_range_id': self.date_range_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['sale.order.report.pfb']
        report = model.create(self._prepare_wt_report())
        return report.print_report(report_type)
