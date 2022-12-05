# -*- coding: utf-8 -*-
{
    'name': "PFB Report Fin",

    'summary': """""",

    'description': """""",

    'author': "PP",
    'website': "",
    'category': 'Report',
    'version': '12.0.1',
    'depends': ['base',
                'fin_system',
                'report_xlsx_helper'],
    'data': [
        'data/paper_format.xml',
        'data/report_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/views_wizard/report_fin_wizard_1.xml',
        'wizard/views_wizard/detailed_budget_report_wizard.xml',
        'views/report_fin.xml',
        'reports/template/detailed_budget_report.xml',
    ],
    'installable': True,
}