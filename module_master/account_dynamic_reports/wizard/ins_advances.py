from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date , time

import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from operator import itemgetter


class Insiadvances(models.TransientModel):
    _name = "ins.advances"

    @api.model
    def _get_default_company(self):
        return self.env.user.company_id

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, 'Advances Report'))
        return res

    date_from = fields.Date(
        string='Start date', default=datetime(datetime.today().year, 1, 1).strftime("%Y-%m-%d")
    )
    date_to = fields.Date(
        string='End date', default=datetime(datetime.today().year, 12, 31).strftime("%Y-%m-%d")
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=_get_default_company
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        # default=_get_default_company
    )
    number = fields.Char(
        string='Number',
    )

    def validate_data(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('"Date from" must be less than or equal to "Date to"'))
        return True

    def get_report_datas(self, default_filters={}):
        '''
        Main method for pdf, xlsx and js calls
        :param default_filters: Use this while calling from other methods. Just a dict
        :return: All the datas for GL
        '''
        if self.validate_data():
            data = self.get_filters(default_filters)
            filters = self.process_filters(data)
            account_lines, line_total = self.process_data(data)
            return filters, account_lines, line_total

    def workdays(self,d, end, excluded=(6, 7)):
        days = []
        while d <= end:
            # print(d.isoweekday())
            if d.isoweekday() not in excluded:
                days.append(d)
            d += timedelta(days=1)

        return days

    def _compute_amount_clear(self,advance):
        amount_remaining = advance.amount_total
        amount_clear = 0.0

        clearing = self.env["account.advance.clear"].search([('advance_id', '=', advance.id)])
        for clear in clearing:
            if clear.state == "posted":
                amount_remaining -= clear.amount_total + (clear.recv_total - clear.paid_total)
                # print(amount_remaining)
                amount_clear += clear.amount_total#clear.recv_total - clear.paid_total #700
                # print(amount_clear)
        if amount_remaining <= 0.0:
            amount_remaining = 0.0
        if amount_clear <= 0.0 or amount_remaining == 0.0:
            amount_clear = 0.0

        if advance.state == "confirmed":
            amount_remaining = advance.amount_total - amount_clear
            amount_clear = amount_clear
        if advance.state == "done":
            amount_remaining = amount_clear
            amount_clear = advance.amount_total - amount_clear

        return amount_clear

    def process_data(self, data):

        if data:
            cr = self.env.cr
            search_domain = []
            lines = []
            company_id = self.env.user.company_id
            company_currency_id = company_id.currency_id

            if data.get('number', False):
                search_domain += [('name', '=', data.get('number'))]
            if data.get('employee_id', 0):
                search_domain += [('employee_id', '=', data.get('employee_id'))]
            if data.get('date_from',False):
                search_domain += [('date', '>=', data.get('date_from'))]
            if data.get('date_to', False):
                search_domain += [('date', '<=', data.get('date_to'))]

            search_domain += [('state', '=', 'done')]

            # 38
            # search_domain += [('id', '=', 74)]
            due_date = contract_end = action_date201 = fin_date201 = fin_remark = ''
            total_contract_amount = 0
            doc_date = 0

            advance_obj = self.env['account.advance'].search(search_domain)

            if advance_obj:
                for advance in advance_obj:
                    if advance.advance_request_id.due_date:
                        due_date = advance.advance_request_id.due_date.strftime("%d-%m-%Y")

                    if advance.advance_request_id.contract_end:
                        contract_end = advance.advance_request_id.contract_end.strftime("%d-%m-%Y")

                        today = date.today()
                        lastdate = advance.advance_request_id.contract_end
                        # delta = today - lastdate
                        workdate = self.workdays(lastdate,today)
                        doc_date = len(workdate)
                        # ลบวันหยุด ทั้งปี ปัจจุบัน
                        holiday = self.env["hr.holidays.public"].search([("year", "=", date.today().year)])
                        # print(holiday)
                        if holiday:
                            holidays = self.env["hr.holidays.public.line"].search([("year_id", "=", holiday.id)])
                            doc_date = doc_date - len(holidays)
                        fin_remark = ''
                        for line in advance.advance_request_id.contract_no.fin_lines:
                            if line.fin100_id:
                                system_201 = self.env["fw_pfb_fin_system_201_line"].search(
                                    [("fin100_number", "=", line.fin100_id.id),("fin401_id", "=", advance.advance_request_id.contract_no.id)])
                                for li201 in system_201:
                                    fin_remark = li201.fin_id.fin_remark or ''
                                    if li201.fin_id.fin_date:
                                        fin_date201 = li201.fin_id.fin_date.strftime("%d-%m-%Y")
                                    for app201 in li201.fin_id.approver:
                                        if app201.action_date:
                                            action_date201 = app201.action_date.strftime("%d-%m-%Y")

                    total_contract_amount += advance.advance_request_id.contract_amount

                    lines.append({
                        'name': advance.advance_request_id.contract_no.fin_no or '',
                        'due_date': due_date,
                        'employee': advance.advance_request_id.employee_id.name or '',
                        'department': advance.advance_request_id.department.name or '',
                        'contract_amount': advance.advance_request_id.contract_amount or 0.0,
                        'date': advance.date.strftime("%d-%m-%Y") or '',
                        'amount_clear': self._compute_amount_clear(advance),
                        'fin_date201': fin_date201,
                        'action_date201': action_date201,
                        'fin_remark201': fin_remark,
                        'contract_end': contract_end,
                        'doc_date':doc_date,
                        'company_currency_id': company_currency_id.id,
                    })

                # print(lines)
                line_total = {
                    'company_currency_id': company_currency_id.id,
                    'total_contract_amount': total_contract_amount,
                }
            else:
                # print('else')
                lines.append({
                    'name': '',
                    'due_date': '',
                    'employee': '',
                    'department': '',
                    'contract_amount': 0.0,
                    'date': '',
                    'fin_date201': '',
                    'action_date201': '',
                    'fin_remark201': '',
                    'contract_end': '',
                    'doc_date': doc_date,
                    'company_currency_id': company_currency_id.id,
                })
                line_total = {
                    'company_currency_id': company_currency_id.id,
                    'total_contract_amount': 0,
                }

            return [lines, line_total]

    def process_filters(self, data):
        ''' To show on report headers'''
        filters = {}

        if data.get('date_from') > data.get('date_to'):
            raise ValidationError(_('From date must not be less than to date'))

        if data.get('date_from', False):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to', False):
            filters['date_to'] = data.get('date_to')

        if data.get('employee_id'):
            filters['employee'] = self.env['hr.employee'].browse(data.get('employee_id')).mapped('name')[0]
        else:
            filters['employee'] = ''

        return filters

    def get_filters(self, default_filters={}):

        company_id = self.env.user.company_id
        company_domain = [('company_id', '=', company_id.id)]

        # journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        # analytics = self.analytic_ids if self.analytic_ids else self.env['account.analytic.account'].search(company_domain)
        employee_id = self.employee_id.id or 0
        filter_dict = {
            # 'employee' : self.env['hr.employee'].browse(employee_id).mapped('name')[0],
            'employee_id': self.employee_id.id,
            'number': self.number,
            'company_id': self.company_id and self.company_id.id or False,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        filter_dict.update(default_filters)
        return filter_dict

    def action_pdf(self):
        # default_filters = {
        #     'employee_id': self.employee_id.id,
        #     'number': self.number,
        #     'company_id': self.company_id and self.company_id.id or False,
        #     'date_from': self.date_from,
        #     'date_to': self.date_to,
        # }
        filters, account_lines, line_total = self.get_report_datas()
        print('filters---action_pdf')
        print(filters)
        print(account_lines)
        print(line_total)
        # filters.update(default_filters)
        return self.env.ref(
            'account_dynamic_reports'
            '.action_advances').with_context(landscape=True).report_action(
            self, data={
                        'account_data': account_lines,
                        'line_total': line_total,
                        'filter_data': filters
                        })

    def action_xlsx(self):
        raise UserError(_('Please install a free module "dynamic_xlsx".'
                          'You can get it by contacting "pycustech@gmail.com". It is free'))

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Advances',
            'tag': 'dynamic.advances',
            'context': {'wizard_id': self.id}
        }
        return res
