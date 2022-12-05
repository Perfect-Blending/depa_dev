# # -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.pfb_withholding_tree.models.wt_tree import generate_bg_report
import uuid


class WithHoldingTaxReportWizardInherit(models.TransientModel):
    _inherit = 'withholding.tax.report.wizard'

    @api.multi
    def button_export_html(self):
        domains = []

        if self.date_from:
            domains.append(('date_from', '=', self.date_from))

        if self.date_to:
            domains.append(('date_to', '=', self.date_to))

        if self.income_tax_form:
            domains.append(('income_tax_form', '=', self.income_tax_form))

        newsession = str(uuid.uuid4())
        print(newsession)
        generate_bg_report(self, newsession, domains)

        title = 'Withholding Tax Report'
        report_model = 'pfb.withholding.tax.tree'

        ret = {
            'name': title,
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': report_model,
            'type': 'ir.actions.act_window',
            'domain': [('session', '=', newsession)]
        }

        return ret






