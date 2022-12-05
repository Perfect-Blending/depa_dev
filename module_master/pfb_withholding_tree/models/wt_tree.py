# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


def year_convert(self, convert_date):
    date_converted = convert_date + relativedelta(years=543)
    date_converted = date_converted.strftime('%d/%m/%Y')
    return date_converted


def generate_bg_report(self, session_id, domains):

    filter_date_from = False
    filter_date_to = False
    filter_income_tax_form = False

    for each in domains:
        # print each
        if each and each[0] == 'date_from':
            filter_date_from = each[2]
        elif each and each[0] == 'date_to':
            filter_date_to = each[2]
        elif each and each[0] == 'income_tax_form':
            filter_income_tax_form = each[2]

    data = {}
    data['form'] = {'date_from': filter_date_from,
                    'date_to': filter_date_to,
                    'income_tax_form': filter_income_tax_form,
                    }

    used_context = {}
    used_context['income_tax_form'] = filter_income_tax_form or False
    used_context['date_from'] = filter_date_from or False
    used_context['date_to'] = filter_date_to or False
    used_context['lang'] = self.env.context.get('lang', 'en_US')

    for each in self.env['bione.wht.line'].search([
        ('wht_id.date_doc', '>=', filter_date_from),
        ('wht_id.date_doc', '<=', filter_date_to),
        ('wht_id.wht_kind', '=', filter_income_tax_form)]):
        _write_bg_report(self, session_id, each, used_context)


def _write_bg_report(self, session_id, each, used_context=None):

    # Summary
    dat = {
        'number_wt': each.wht_id.name,
        'date': each.wht_id.date_doc,
        'supplier': each.wht_id.partner_id.name,
        'vat': each.wht_id.partner_id.vat,
        'street': each.wht_id.partner_id.street,
        'street2': each.wht_id.partner_id.street2,
        'city': each.wht_id.partner_id.city,
        'zip': each.wht_id.partner_id.zip,
        'branch': each.wht_id.partner_id.branch,
        'wt_cert_income_desc': each.wht_type_id.name,
        'comment': each.note,
        'wt_percent': each.percent,
        'base': each.base_amount,
        'amount': each.tax,
        'pnd': each.wht_id.wht_kind,
        # 'tax_payer': each.wht_id.tax_payer,
        # 'payment_id': each.wht_id.payment_id and each.wht_id.payment_id.name or each.wht_id.ref_move_id.name,
        'session': session_id,
    }

    self.env['pfb.withholding.tax.tree'].create(dat)


class WithholdingTaxTree(models.TransientModel):
    _name = 'pfb.withholding.tax.tree'

    number_wt = fields.Char(string="Number WT")
    vat = fields.Char(string="VAT")
    supplier = fields.Char(string="Supplier")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip")
    branch = fields.Char(string="Branch")
    date = fields.Date(string="Date")
    wt_cert_income_desc = fields.Char(string="Cert Income")
    comment = fields.Char(string="Comment")
    wt_percent = fields.Float(string="%")
    base = fields.Float(string="Base Amount")
    amount = fields.Float(string="Tax Amount")
    # tax_payer = fields.Char(string="% ")
    pnd = fields.Char(string="PND")
    session = fields.Char()
    head = fields.Boolean()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        required=True,
        ondelete='cascade',
    )

    @api.multi
    def to_fist_name(self, fist):
        fist_name = []
        len_str = 0
        for i in fist:
            if i == ' ':
                return ''.join(fist_name)
            fist_name.append(i)
            len_str += 1
        return ''.join(fist_name)

    def to_last_name(self, last):
        last_name = []
        len_str = 0
        count_name = len(last)
        for i in last:
            # print(i)
            if i == ' ':
                last_name.append(last[len_str:count_name])
                return ''.join(last_name)
            len_str += 1
        return ''.join(last_name)

    def to_last_name2(self, last):
        last_name = []
        len_str = 0
        count_name = len(last)
        for i in last:
            # print(i)
            if i == ' ':
                last_name.append(last[len_str:count_name])
                return ''.join(last_name)
            len_str += 1
        return ''.join(last_name)

