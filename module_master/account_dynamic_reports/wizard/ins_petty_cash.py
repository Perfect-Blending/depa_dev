from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from operator import itemgetter


class InsPettyCash(models.TransientModel):
    _name = "ins.petty.cash"

    @api.model
    def _get_default_company(self):
        return self.env.user.company_id

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, 'Petty Cash Report'))
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
    fund_id = fields.Many2one(
        'account.petty.fund', string='Petty Cash Fund',required=True
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
            # account_lines, retained, subtotal = self.process_data(data)
            account_lines,line_total = self.process_data(data)

            return filters, account_lines,line_total #, retained, subtotal

    def process_data(self, data):
        # print(data)
        if data:
            cr = self.env.cr
            search_domain = []
            params = self.env['ir.config_parameter'].sudo()
            company_id = self.env.user.company_id
            company_currency_id = company_id.currency_id

            # WHERE = " payment.id = 105  "

            WHERE = '  l.account_id IN (SELECT DISTINCT account_id FROM account_petty_fund) '
            WHERE += ' AND fund.id = %s' % data.get('fund_id',0)

            if data.get('date_from') and data.get('date_to'):
                WHERE += "  AND move.date >= '%s'" % data.get('date_from')
                WHERE += "  AND move.date <= '%s'" % data.get('date_to')

            sql = (''' 	    
                   SELECT 
                        move.id
                        ,move.date
                        ,invoice.id as invoice_id
                        ,invoice.number as invoice_name
                        ,payment.id as payment_id
                        ,payment.name as payment_name
                        ,employee.name as payment_employee
                        ,fund.account_id as account_id
                        ,COALESCE(SUM(l.debit),0) AS debit
                        ,COALESCE(SUM(l.credit),0) AS credit
                         FROM account_move   move
                            LEFT JOIN account_move_line   l
                                ON move.id = l.move_id  
                            LEFT JOIN account_invoice   invoice
                                ON move.id = invoice.move_id  
                            LEFT JOIN account_petty_payment   payment
                                ON move.id = payment.move_id
                            LEFT JOIN hr_employee   employee
                                ON employee.id = payment.employee_id
                            LEFT JOIN account_petty_fund  fund
                                ON l.account_id = fund.account_id
                    WHERE %s 
                    GROUP BY 
                        move.id
                        ,move.date
                        ,invoice.id
                        ,invoice.name
                        ,payment.id
                        ,payment.name
                        ,employee.name
                        ,fund.account_id
 		            ''') % WHERE

            cr.execute(sql)
            result = cr.dictfetchall()
            petty_lines = []
            receipt_amount = payment_amount = balance_receipt = balanc_payment = 0.0
            t_column_1 = t_column_2 = t_column_3 = t_column_4 = t_column_5 = t_column_6 = t_column_7 = 0.0
            t_column_8 = t_column_9 = t_column_10 = t_column_11 = t_column_12 = 0.0
            account_etc = desc = ''
            total_receipt_amount = total_payment_amount = balanc_payment = 0.0
            for move in result:
                move_id = move['id']
                invoice_id = move['invoice_id']
                payment_id = move['payment_id']
                account_id = move['account_id']
                receipt_amount = move['debit']
                payment_amount = move['credit']
                balance_receipt += receipt_amount - payment_amount
                total_receipt_amount += receipt_amount
                total_payment_amount += payment_amount

                column_1 = column_2 = column_3 = column_4 = column_5 = column_6 = column_7 = 0.0
                column_8 = column_9 = column_10 = column_11 = column_12 = 0.0
                account_etc = []
                if payment_id:
                    payment = self.env['account.petty.payment'].browse(payment_id)
                    # payment_amount = sum(line.credit for line in payment.move_id.line_ids)
                    desc = payment.desc or ''



                    # xx = self.env['account.account'].search(['|', ('name', 'like', 'ค่าไปรษณีย'), ('name', 'like', 'ค่าอากรแสตมป์')])
                    # print(xx)
                    # print([x.id for x in self.env['account.account'].search(['|', ('name', 'like', 'ค่าไปรษณีย'), ('name', 'like', 'ค่าอากรแสตมป์')])])
                    account_ids = []
                    for line in payment.move_id.line_ids:

                        amount = round(line.debit,2) if line.debit > 0 else round(line.credit,2)
                        if line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าพาหนะ')])]:
                            account_ids.append(line.account_id.id)
                            column_1 = column_1 + amount
                            t_column_1 = t_column_1 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าทางด่วน')])]:
                            account_ids.append(line.account_id.id)
                            column_2 = column_2 + amount
                            t_column_2 = t_column_2 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'วัสดุสำนักงาน')])]:
                            account_ids.append(line.account_id.id)
                            column_3 = column_3 + amount
                            t_column_3 = t_column_3 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าโทรศัพท์')])]:
                            account_ids.append(line.account_id.id)
                            column_4 = column_4 + amount
                            t_column_4 = t_column_4 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search(['|',('name', 'like' , 'ค่าไปรษณีย'),('name', 'like', 'ค่าอากรแสตมป์')])]:
                            account_ids.append(line.account_id.id)
                            column_5 = column_5 + amount
                            t_column_5 = t_column_5 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าใช้จ่ายจัดประชุม')])]:
                            account_ids.append(line.account_id.id)
                            column_6 = column_6 + amount
                            t_column_6 = t_column_6 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าเบี้ยเลี้ยง')])]:
                            account_ids.append(line.account_id.id)
                            column_7 = column_7 + amount
                            t_column_7 = t_column_7 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าที่พัก')])]:
                            account_ids.append(line.account_id.id)
                            column_8 = column_8 + amount
                            t_column_8 = t_column_8 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ค่าใช้จ่ายจัดงาน')])]:
                            account_ids.append(line.account_id.id)
                            column_9 = column_9 + amount
                            t_column_9 = t_column_9 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ส่วนต่างจากการจ่ายชำระ')])]:
                            account_ids.append(line.account_id.id)
                            column_10 = column_10 + amount
                            t_column_10 = t_column_10 + amount
                        elif line.account_id.id in [x.id for x in self.env['account.account'].search([('name', 'like', 'ภาษีหัก ณ ที่จ่าย')])]:
                            account_ids.append(line.account_id.id)
                            column_11 = column_11 + amount
                            t_column_11 = t_column_11 + amount
                        else:
                            print(account_ids)
                            print(account_id)
                            # if account_id not in account_ids:
                            if account_id != line.account_id.id:
                                account_etc.append(line.account_id.name)

                                column_12 = payment.amount_total  # sum(line.price_unit * line.quantity for line in payment.lines) + sum(line.amount_tax for line in payment.vat_lines) - sum(line.tax for line in payment.wht_lines)
                                t_column_12 = t_column_12 + payment.amount_total


                if invoice_id:
                    invoice = self.env['account.invoice'].browse(invoice_id)
                    for line in invoice.invoice_line_ids:
                        desc = line.name or ''

                # print(desc)
                #หารายการ Payment #
                petty_lines.append({
                    'date': move['date'].strftime("%d-%m-%Y"),
                    'name': move['invoice_name'] or move['payment_name'],
                    'employee': move['payment_employee'],#x.employee_id.name,
                    'company_currency_id': company_currency_id.id,
                    'receipt_amount': receipt_amount,
                    'payment_amount': payment_amount,
                    'balance': balance_receipt,
                    'column_1': column_1,
                    'column_2': column_2,
                    'column_3': column_3,
                    'column_4': column_4,
                    'column_5': column_5,
                    'column_6': column_6,
                    'column_7': column_7,
                    'column_8': column_8,
                    'column_9': column_9,
                    'column_10': column_10,
                    'column_11': column_11,
                    'column_12': column_12,
                    'account_etc': ", ".join(account_etc),
                    'desc': desc,
                })

            line_total = {
                'company_currency_id': company_currency_id.id,
                'total_receipt_amount': total_receipt_amount,
                'total_payment_amount': total_payment_amount,
                'total_balance_receipt': balance_receipt,
                't_column_1': t_column_1,
                't_column_2': t_column_2,
                't_column_3': t_column_3,
                't_column_4': t_column_4,
                't_column_5': t_column_5,
                't_column_6': t_column_6,
                't_column_7': t_column_7,
                't_column_8': t_column_8,
                't_column_9': t_column_9,
                't_column_10': t_column_10,
                't_column_11': t_column_11,
                't_column_12': t_column_12,
            }

            subtotal = 0.0
            # print('--------------->')
            # print([petty_lines, retained, subtotal])
            # print('--------------->+')
            return [petty_lines , line_total]

    def process_filters(self, data):
        ''' To show on report headers'''
        filters = {}

        if data.get('date_from') > data.get('date_to'):
            raise ValidationError(_('From date must not be less than to date'))
        if data.get('fund_id',False) == False:
            raise ValidationError(_('Please specify fund'))

        if data.get('date_from', False):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to', False):
            filters['date_to'] = data.get('date_to')

        if data.get('fund_id'):
            filters['fund'] = self.env['account.petty.fund'].browse(data.get('fund_id')).mapped('name')[0]
        else:
            filters['fund'] = ''

        return filters

    def get_filters(self, default_filters={}):

        company_id = self.env.user.company_id
        company_domain = [('company_id', '=', company_id.id)]

        # journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        # analytics = self.analytic_ids if self.analytic_ids else self.env['account.analytic.account'].search(company_domain)

        filter_dict = {
            'fund' : self.env['account.petty.fund'].browse(self.fund_id.id).mapped('name')[0],
            'fund_id': self.fund_id.id,
            'company_id': self.company_id and self.company_id.id or False,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        filter_dict.update(default_filters)
        return filter_dict

    def action_pdf(self):
        filters, account_lines,line_total = self.get_report_datas()

        return self.env.ref(
            'account_dynamic_reports'
            '.action_petty_cash').with_context(landscape=True).report_action(
            self, data={'account_data': account_lines,
                        'line_total': line_total,
                        'filter_data': filters
                        })

    def action_xlsx(self):
        raise UserError(_('Please install a free module "dynamic_xlsx".'
                          'You can get it by contacting "pycustech@gmail.com". It is free'))

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Petty Cash Report',
            'tag': 'dynamic.petty.cash',
            'context': {'wizard_id': self.id}
        }
        return res
