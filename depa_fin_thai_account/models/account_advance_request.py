# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AccountAdvanceRequest(models.Model):
    _inherit = "account.advance.request"

    title_id = fields.Many2one('fw_pfb_objective', 'วัตถุประสงค์', required=False)
    contract_no = fields.Many2one("fw_pfb_fin_system_401", 'Contract No', required=False,
                              domain=[('state', '=', 'completed')])
    loan_period = fields.Selection([('7days_from_activity_end_date', '7 Business Days From Activity End date '),
                                ('7days_from_activity_end_date_domestic',
                                 '7 Business Days From Activity End date For Work Domestic'),
                                ('15days_from_activity_end_date_oversea',
                                 '15 Business Days From Activity End date For Work Overseas')],
                               string='Loan period')

    @api.onchange('contract_no')
    def onchange_contract_no(self):
        self.lines = [(5, 0, 0)]
        fin_lines = []

        # , related='contract_no.fin_objective'
        if self.contract_no:
            self.date_due = self.contract_no.fin_date  # related='contract_no.fin_date'
            self.title_id = self.contract_no.fin_objective
            self.employee_id = self.contract_no.requester
            self.date = self.contract_no.fin_date
            self.user_id = self.contract_no.requester.user_id
            self.loan_period = self.contract_no.loan_period
            self.department = self.contract_no.department
            self.contract_amount = self.contract_no.price_total
            self.contract_start = self.contract_no.activity_end_date
            self.contract_end = self.contract_no.fin_end_date
            self.contract_details = self.contract_no.objective
            self.memo_no = self.contract_no.fin_ref

            if self.contract_no.approver:
                for appr in self.contract_no.approver:
                    self.due_date = appr.action_date

            if self.contract_no.fin_lines:
                analytic_account_id = 0
                for line in self.contract_no.fin_lines:
                    # print(line)
                    for fin in line.fin100_id.fin_lines:  # .fw_pfb_fin_system_100_line:
                        # print(fin)
                        if fin.product_id.id == line.product_id.id:
                            analytic_account_id = fin.projects_and_plan.id

                    line_vals = {
                        'product_id': line.product_id.id,
                        'name': line.description or line.product_id.name,
                        'amount': line.price_subtotal,
                        'analytic_account_id': analytic_account_id
                    }
                    fin_lines.append((0, 0, line_vals))

                self.lines = fin_lines

    @api.multi
    def _create_account_advance(self):

        for obj in self:
            vals = {
                'name': '',
                'date': self.date,
                'date_due': self.date_due,
                'description': self.description,
                'note': self.notes,
                'employee_id': self.employee_id.id,
                'company_id': self.company_id.id,
                'currency_rate': self.currency_rate,
                'currency_rate_date': self.currency_rate_date,
                'currency_id': self.currency_id.id,
                'amount_total': self.amount_total,
                'ref': self.name,
                'advance_request_id': self.id,
                'lines': [],
                'title_id': self.title_id.id,
            }
            for line in self.lines:
                line_vals = {
                    'name': line.name,
                    'amount': line.amount,
                    'product_id': line.product_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                }
                vals['lines'].append((0, 0, line_vals))
            advance = self.env['account.advance'].create(vals)
        return advance


