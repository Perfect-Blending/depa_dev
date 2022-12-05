from odoo import api, models
from bahttext import bahttext
from dateutil.relativedelta import relativedelta
from num2words import num2words


class WHTForm(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.wht_pdf_report_pdf'


    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['bione.wht'].browse(docids)
        for o in docs:
            print(o)
            id = []
            id.append(o)
            print(id)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'bione.wht',
            'docs': docs,
            'id': id,
        }


class WHT2Form(models.AbstractModel):
    _name = 'report.all_qweb_form_depa.wht2_pdf_report_pdf'


    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        print(self)
        for ids in self:
            print(ids)
        docs = self.env['bione.wht'].browse(docids)
        id = []
        for o in docs:
            for line in o.line_ids:
                id.append(line)
                print(id)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'bione.wht',
            'docs': docs,
            'id': id,
        }


class BioneWhtFix(models.Model):
    _inherit = 'bione.wht'

    @api.multi
    def amount_text(self, amount):
        try:
            return num2words(amount, to='currency', lang='th')
        except NotImplementedError:
            return num2words(amount, to='currency', lang='en')

    @api.multi
    def _compute_sum_type_other(self, lines, ttype):
        base_type_other = sum(lines.filtered(
            lambda l: l.wht_type_id.id in [15]).mapped(ttype))
        return base_type_other

    @api.multi
    def _compute_desc_type_other(self, lines, ttype):
        base_type_other = lines.filtered(
            lambda l: l.wht_type_id.id in [15]).mapped(ttype)
        desc = ", ".join(base_type_other)
        return desc