from odoo import models, fields, api
from odoo.addons.pfb_report_fin.models.report_fin import generate_bg_report_fin
import uuid


class NewReportFin1Wizard(models.TransientModel):
    _name = 'pfb.report.fin.wizard'

    fiscal_year = fields.Many2one('fw_pfb_fin_system_fiscal_year', string="Fiscal Year")

    @api.multi
    def button_export_html(self):
        domains = []
        if self.fiscal_year:
            domains.append(('fiscal_year', '=', self.fiscal_year.fiscal_year))
        newsession = str(uuid.uuid4())
        generate_bg_report_fin(self, newsession, domains)
        title = 'Report Fin'
        report_model = 'pfb.report.fin'
        res = {
            'name': title,
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': report_model,
            'type': 'ir.actions.act_window',
            'domain': [('session', '=', newsession)]

        }
        return res

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        report_type = 'xlsx'
        return self._export(report_type)

    def _prepare_fin_report(self):
        self.ensure_one()
        return {
            'fiscal_year': self.fiscal_year.fiscal_year,
        }

    def _export(self, report_type):
        model = self.env['report.pfb.fin.report']
        report = model.create(self._prepare_fin_report())
        return report.print_report(report_type)




