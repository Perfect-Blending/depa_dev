# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT
from random import randrange

RETURN_STATE = [
    'cancelled',
    'reject'
]


class AccountAnalyticAccountExtensionInherit(models.Model):
    _inherit = 'account.analytic.account'

    fin100_project_ids = fields.One2many('fw_pfb_fin_system_100_projects', 'projects_and_plan', 'FIN EXPENSE LINES')
    fin100_project_ids_ready = fields.One2many('fw_pfb_fin_system_100_projects', string='FIN EXPENSE LINES READY',
                                               compute="_get_fin100_datas")
    fin100_ids = fields.One2many('fw_pfb_fin_system_100', string='FIN100', compute="_get_fin100_datas")
    budget_balance = fields.Float("Balance", readonly=True, compute='_compute_project_balance', store=True)
    budget_balance_percent = fields.Float("Balance in Percent", readonly=True, compute='_compute_project_balance',
                                          store=True)
    budget_reserve = fields.Float(
        string='Reserve',
        compute='_compute_project_balance',
        readonly=True,
        store=True,
    )
    budget_return = fields.Float(
        string='Return',
        compute='_compute_project_balance',
        readonly=True,
        store=True,
    )
    dummy = fields.Integer(string="dummy")

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     print('NAME SEARCH')
    #     if not args:
    #         args = []
    #     if name:
    #         analytic_ids = self._search(args, limit=limit)
    #     return self.browse(analytic_ids).name_get()
    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.fiscal_year.fiscal_year:
                name += '[' + str(rec.fiscal_year.fiscal_year) + ']'
            if rec.code:
                name += '[' + str(rec.code) + '] '
            if rec.name:
                name += str(rec.name)
            result.append((rec.id, name))
        return result

    @api.depends('fin100_project_ids', 'fin100_project_ids.projects_reserve', 'fin100_project_ids.projects_residual',
                 'fin100_project_ids.fin_id.state', 'dummy')
    def _compute_project_balance(self):
        print('FIN_100._compute_project_balance')
        for obj in self:
            budget_return = 0.0
            budget_reserve = 0.0
            budget_balance = budget_balance_percent = 0.0
            own_expense = child_expense = 0.0

            # get own expense
            for line in obj.fin100_project_ids_ready:
                if not line.fin_id.is_new:
                    own_expense += line.projects_reserve or 0.0

            for line in obj.fin100_project_ids:
                if line.fin_id.state in RETURN_STATE:
                    budget_return += line.projects_reserve
                    own_expense += line.projects_reserve
                else:
                    if not line.fin_id.is_fin_open:
                        budget_return += line.projects_return

            budget_reserve += own_expense
            budget_balance = obj.budget - own_expense - child_expense + budget_return
            budget_balance_percent = budget_balance * 100 / (obj.budget or 1)
            obj.update({
                'budget_balance': budget_balance,
                'budget_balance_percent': budget_balance_percent,
                'budget_reserve': own_expense,
                'budget_return': budget_return,
            })
        self.button_force_compute_fin100_lines()

    @api.depends('fin100_project_ids')
    def _get_fin100_datas(self):
        for obj in self:
            obj.fin100_project_ids_ready = obj.fin100_project_ids.filtered(
                lambda x: x.fin100_state not in ['cancelled', 'reject'])
            obj.fin100_ids = obj.fin100_project_ids.mapped('fin_id')

    @api.multi
    def button_force_compute_fin100_lines(self):
        for project in self:
            budget = project.budget or 0.0
            for line in project.fin100_project_ids.sorted(key=lambda x: x.fin_id.fin_date and x.fin_id.fin_no):
                line.projects_residual = budget
                line.projects_residual_amount = budget - line.projects_reserve
                budget -= line.projects_reserve
                line.projects_residual_amount = line.projects_residual_amount if (
                            line.fin_id.state not in RETURN_STATE and line.fin_id.is_fin_open) else line.projects_residual_amount + line.projects_return
                budget = budget if (
                            line.fin_id.state not in RETURN_STATE and line.fin_id.is_fin_open) else budget + line.projects_return
                # line.projects_residual_amount = (budget - line.projects_reserve) if line.fin_id.state not in RETURN_STATE else (budget - line.projects_reserve + line.projects_return)
                # budget -= (line.projects_reserve) if line.fin_id.state not in RETURN_STATE else (line.projects_reserve + line.projects_return)
        self.button_dummy()
        return True

    @api.multi
    def button_force_reset_fin100_lines(self):
        for obj in self:
            for fin100_project in obj.fin100_project_ids:
                projects_return = 0.0
                if fin100_project.fin_id.state in RETURN_STATE or not fin100_project.fin_id.is_fin_open:
                    projects_return = fin100_project.projects_return
                if fin100_project.fin_id.state in RETURN_STATE and fin100_project.fin_id.is_fin_open:
                    projects_return = fin100_project.projects_reserve
                fin100_project.write({
                    'projects_residual': 0.0,
                    'projects_residual_amount': 0.0,
                    'projects_return': projects_return,
                })
                obj.button_dummy()
        return True

    @api.multi
    def button_dummy(self):
        for obj in self:
            obj.dummy = randrange(1000001)
        return True

    @api.multi
    def xname_get(self):
        if not self._context.get('show_remaining'):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(AccountAnalyticAccountExtensionInherit, self).name_get()
        res = []
        for record in self:
            name = record.name
            if record.budget_balance:
                name = "%(name)s (%(count)s)" % {
                    'name': name,
                    'count': _('%g remaining out of %g') % (
                        float_round(record.budget_balance, precision_digits=2) or 0.0,
                        float_round(record.budget, precision_digits=2) or 0.0,
                    )
                }
            res.append((record.id, name))
        return res
