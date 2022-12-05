from odoo import api, models
from dateutil.relativedelta import relativedelta
from bahttext import bahttext


class PrHireForm(models.AbstractModel):
    _name = 'report.pr_hire_qweb.pr_hire_pdf_report_pdf'

    def year_convert(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.request'].browse(docids)
        date_start = ''
        thaibahttext = ''
        count_row = 0
        sum_total = 0
        date_pr = ''
        i = 0
        doc_data = {}
        for doc in docs:
            doc_data[i] = {}
            doc_data[i]['thai_baht_text'] = ''
            doc_data[i]['group'] = []
            doc_data[i]['line_name'] = []
            doc_data[i]['sum_total'] = 0
            doc_data[i]['date_pr'] = ''
            doc_data[i]['date_start'] = ''
            doc_data[i]['des_pr'] = ''
            doc_data[i]['tag'] = ''

            doc_data[i]['name'] = doc.number_pr
            doc_data[i]['analytic_account_id'] = doc.analytic_account_id
            doc_data[i]['analytic_account_code'] = doc.analytic_account_id.code
            doc_data[i]['analytic_account_name'] = doc.analytic_account_id.name
            doc_data[i]['analytic_account_department'] = doc.analytic_account_id.department.name
            doc_data[i]['analytic_account_year'] = doc.analytic_account_id.fiscal_year.fiscal_year
            doc_data[i]['department'] = doc.department_id.name
            doc_data[i]['des_pr'] = doc.description
            # doc_data[i]['fin_number'] = doc.fin_number.fin_no
            doc_data[i]['pr_ck'] = doc.pr_ck
            doc_data[i]['pr3_ck'] = doc.pr3_ck
            doc_data[i]['pr4_ck'] = doc.pr4_ck
            doc_data[i]['pr2_ck'] = doc.pr2_ck
            doc_data[i]['notes_check'] = doc.notes_check
            doc_data[i]['method_of_recruitment'] = doc.method_of_recruitment.name
            doc_data[i]['method_of_recruitment_partner'] = doc.method_of_recruitment.partner_id.name
            doc_data[i]['tag'] = doc.tag_ids.name
            if doc.date_pr:
                doc_data[i]['date_pr'] = self.year_convert(doc.date_pr)
            if doc.date_start:
                doc_data[i]['date_start'] = self.year_convert(doc.date_start)
            for line in doc.line_ids:
                doc_data[i]['group'].append(line)
                doc_data[i]['line_name'].append(line.name)
                doc_data[i]['sum_total'] += line.product_qty * line.estimated_cost
                doc_data[i]['thai_baht_text'] = bahttext(doc_data[i]['sum_total'])
                count_row += 1
                sum_total += line.product_qty * line.estimated_cost

            doc_data[i]['user_create'] = doc.create_uid.partner_id.name
            obj = self.env['hr.employee'].search([
                ('name', '=',  doc_data[i]['user_create']),
            ])
            doc_data[i]['display_name'] = obj.display_name
            doc_data[i]['position'] = obj.job_id.name
            doc_data[i]['create_date'] = self.year_convert(doc.create_date)
            doc_data[i]['approver_name'] = []
            doc_data[i]['approver_job'] = []
            doc_data[i]['approver_date'] = []
            for approver_line in doc.review_ids:
                doc_data[i]['approver_name'].append(approver_line.done_by.name)
                doc_data[i]['approver_date'].append(self.year_convert(approver_line.reviewed_date))
                jop_name = self.env['hr.employee'].search([
                    ('name', '=', doc_data[i]['approver_name']),
                ])
                doc_data[i]['approver_job'].append(jop_name.job_organization.name)
            doc_data[i]['employee_name'] = ''
            doc_data[i]['employee_job'] = ''
            doc_data[i]['fin_number'] = ''
            if doc.fin_number:
                doc_data[i]['fin_number'] = doc.fin_number.fin_no
                doc_data[i]['fin_approver'] = []
                for fin100_line in doc.fin_number.approver:
                    doc_data[i]['fin_approver'].append(fin100_line.employee_id.name)
                employee_obj = self.env['hr.employee'].search([
                    ('name', '=',  doc_data[i]['fin_approver'][0]),
                ])
                doc_data[i]['employee_name'] = employee_obj.display_name
                doc_data[i]['employee_job'] = employee_obj.job_id.name
            thaibahttext = bahttext(sum_total)
            i += 1

            return {
                'doc_ids': docs.ids,
                'doc_model': 'purchase.request',
                'docs': doc_data,
                'date_start': date_start,
                'count_row': count_row,
                'thaibahttext': thaibahttext,
            }
