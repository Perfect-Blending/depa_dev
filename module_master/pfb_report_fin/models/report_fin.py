# -*- coding: utf-8 -*-
from odoo import models, fields, api


def generate_bg_report_fin(self, session_id, domains):
    filter_fiscal_year = False

    for each in domains:
        if each and each[0] == 'fiscal_year':
            filter_fiscal_year = each[2]

    data = {}
    data['form'] = {'fiscal_year': filter_fiscal_year}

    used_context = {}
    used_context['fiscal_year'] = filter_fiscal_year or False
    used_context['lang'] = self.env.context.get('lang', 'en_US')

    for each in self.env['account.analytic.account'].search([('fiscal_year', '=', filter_fiscal_year)]):
        _write_bg_report(self, session_id, each, used_context)


def _write_bg_report(self, session_id, each, used_context=None):
    # Summary
    group = '%s / %s' % (each.group_id.parent_id, each.group_id.name)

    dat = {
        'fiscal_year': each.fiscal_year.fiscal_year,
        'group_id': each.group_id.complete_name,
        'code': each.code,
        'name': each.name,
        'budget': each.budget,
        'budget_reserve': each.budget_reserve,
        'budget_return': each.budget_return,
        'budget_spend': each.budget_spend,
        'budget_balance': each.budget_balance,
        'budget_balance_percent': each.budget_balance_percent,
        'session': session_id,

    }
    print(each)
    self.env['pfb.report.fin'].create(dat)


class PfbReportFin(models.TransientModel):
    _name = 'pfb.report.fin'

    fiscal_year = fields.Char(string='Fiscal Year')
    group_id = fields.Char(string='Group')
    code = fields.Char(string='Reference')
    name = fields.Char(string='Analytic Account')
    budget = fields.Float(string='Budget')
    budget_reserve = fields.Float(string='reserve')
    budget_return = fields.Float(string='return')
    budget_spend = fields.Float(string='Budget Spend')
    budget_balance = fields.Float(string='Balance')
    budget_balance_percent = fields.Float(string='Balance In Percent')
    session = fields.Char()


class FinReport(models.TransientModel):
    _name = 'report.pfb.fin.report'
    _description = 'PFB Fin Report'

    fiscal_year = fields.Char(string='Fiscal Year')

    @api.multi
    def print_report(self, report_type='qweb'):
        self.ensure_one()
        action = report_type == 'xlsx' and self.env.ref(
            'pfb_report_fin.action_finn_report_xlsx')
        return action.report_action(self, config=False)
