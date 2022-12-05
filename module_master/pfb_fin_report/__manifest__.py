# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Fin Report',
    'version': '12.0.1.0.2',
    'author': 'PP',
    'website': '',
    'license': '',
    'category': 'Report',
    'depends': ['base',
                'fin_system',
                'report_xlsx_helper'],
    'data': [
        # 'data/paper_format.xml',
        # 'data/report_data.xml',
        'data/detailed_budget_report.xml',
        'data/budget_usage_report.xml',
        'data/summary_budget_report.xml',
        'wizard/views_wizard/detailed_budget_report_wizard.xml',
        'wizard/views_wizard/budget_usage_report_wizard.xml',
        'wizard/views_wizard/balance_summary_budget_wizard.xml',
        'report/template/detailed_budget_report.xml',
        'report/template/budget_usage_report.xml',

    ],
    'installable': True,
}
