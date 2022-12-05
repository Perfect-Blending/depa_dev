from odoo import api, models
from dateutil.relativedelta import relativedelta


class PfbWithholdingReport(models.AbstractModel):
    _name = 'report.pfb_withholding_tree.report_withholding_tax_qweb'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['pfb.withholding.tax.tree'].browse(docids)
        count = 0
        for doc in docs:
            income_tax_form = doc.pnd
            company = doc.company_id.name
            count += len(doc)

            return {
                'doc_ids': docs.ids,
                'doc_model': 'pfb.withholding.tax.tree',
                'docs': docs,
                'income_tax_form': income_tax_form,
                'company': company,
            }


class PfbWithholdingReport2(models.AbstractModel):
    _name = 'report.pfb_withholding_tree.report_withholding_tax_qweb2'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['pfb.withholding.tax.tree'].browse(docids)
        count = 0
        for doc in docs:
            income_tax_form = doc.pnd
            company = doc.company_id.name
            count += len(doc)

            return {
                'doc_ids': docs.ids,
                'doc_model': 'pfb.withholding.tax.tree',
                'docs': docs,
                'income_tax_form': income_tax_form,
                'company': company,
            }
