# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Expense Report',
    'version': '12.0.1.0.2',
    'author': 'PP',
    'website': '',
    'license': 'AGPL-3',
    'category': 'Expense',
    'depends': ['account',
                'hr_expense',
                ],
    'data': [
            'data/paper_format.xml',
            'data/report_data.xml',
            'wizard/expenses_report_wizard_view.xml',
            'report/report_expenses_pdf.xml',
             ],
    'installable': True,
}
