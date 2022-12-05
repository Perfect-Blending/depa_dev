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

    for each in domains:
        # print each
        if each and each[0] == 'date_from':
            filter_date_from = each[2]
        elif each and each[0] == 'date_to':
            filter_date_to = each[2]

    data = {}
    data['form'] = {'date_from': filter_date_from,
                    'date_to': filter_date_to,
                    }

    used_context = {}
    used_context['date_from'] = filter_date_from or False
    used_context['date_to'] = filter_date_to or False
    used_context['lang'] = self.env.context.get('lang', 'en_US')

    for each in self.env['bione.account.vat'].search([
        ('docdat', '>=', filter_date_from),
        ('docdat', '<=', filter_date_to),
        ('customer_receipts_id.state', '=', 'post'),
        ('vat_type', '=', 'sale'), ]):
        _write_bg_report(self, session_id, each, used_context)

    for each2 in self.env['bione.account.vat'].search([
        ('docdat', '>=', filter_date_from),
        ('docdat', '<=', filter_date_to),
        ('customer_payment_id.state', '=', 'post'),
        ('vat_type', '=', 'sale'), ]):
        _write_bg_report(self, session_id, each2, used_context)

    for cr in self.env['account.invoice'].search([
        ('date_invoice', '>=', filter_date_from),
        ('date_invoice', '<=', filter_date_to),
        ('type', '=', 'out_refund'),
        ('state', 'in', ['paid', 'open']),
    ]):
        _write_cr_report(self, session_id, cr, used_context)


def _write_bg_report(self, session_id, each, used_context=None):
    # Summary
    dat = {
        'number_tax': each.name,
        'date_dat': each.docdat,
        'date_vatprd': each.vatprd,
        'vat': each.vat_period,
        'partner': each.partner_id.name,
        'partner_vat': each.taxid,
        'branch': each.depcod,
        'amount_untaxed': each.amount_untaxed,
        'amount_tax': each.amount_tax,
        'amount_total': each.amount_total,
        'remark': each.remark,
        'number_jou': each.customer_payment_id.move_id.name,
        'date_jou': each.customer_payment_id.move_id.date,
        'session': session_id,
    }

    self.env['pfb.sale.order.tree'].create(dat)


def _write_bg_report(self, session_id, each2, used_context=None):
    # Summary
    dat = {
        'number_tax': each2.name,
        'date_dat': each2.docdat,
        'date_vatprd': each2.vatprd,
        'vat': each2.vat_period,
        'partner': each2.partner_id.name,
        'partner_vat': each2.taxid,
        'branch': each2.depcod,
        'amount_untaxed': each2.amount_untaxed,
        'amount_tax': each2.amount_tax,
        'amount_total': each2.amount_total,
        'remark': each2.remark,
        'number_jou': each2.customer_payment_id.move_id.name,
        'date_jou': each2.customer_payment_id.move_id.date,
        'session': session_id,
    }

    self.env['pfb.sale.order.tree'].create(dat)


def _write_cr_report(self, session_id, cr, used_context=None):
    # Summary
    code = ''
    for tax in cr.tax_line_ids:
        print(tax.account_id.code)
        code = tax.account_id.code
    if code == '21999-99-02-001':
        dat = {
            'number_tax': cr.number,
            'date_dat': cr.date_invoice,
            'date_vatprd': cr.date_due,
            'vat': '',
            'partner': cr.partner_id.name,
            'partner_vat': cr.partner_id.vat,
            'branch': cr.partner_id.branch,
            'amount_untaxed': - cr.amount_untaxed,
            'amount_tax': - cr.amount_tax,
            'amount_total': - cr.amount_total,
            'remark': '',
            'number_jou': '',
            'date_jou': cr.date_due,
            'session': session_id,
        }

        self.env['pfb.sale.order.tree'].create(dat)


class SaleOrderTree(models.TransientModel):
    _name = 'pfb.sale.order.tree'

    number_tax = fields.Char(string="เลขที่ใบกำกับภาษี")
    date_dat = fields.Date(string="ลงวันที่")
    date_vatprd = fields.Date(string="วันที่ยื่น")
    vat = fields.Char(string="งวดที่")
    partner = fields.Char(string="พาร์ทเนอร์")
    partner_vat = fields.Char(string="เลขประจำตัวผู้เสียภาษี")
    branch = fields.Char(string="รหัสสาขา")
    amount_untaxed = fields.Float(string="ยอดก่อนภาษี")
    amount_tax = fields.Float(string="ภาษี")
    amount_total = fields.Float(string="รวมเงิน")
    remark = fields.Char(string="หมายเหตุ")
    number_jou = fields.Char(string="เลขที่ใบสำคัญ")
    date_jou = fields.Date(string="วันที่ใบสำคัญ")
    session = fields.Char()
    head = fields.Boolean()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        required=True,
        ondelete='cascade',
    )
