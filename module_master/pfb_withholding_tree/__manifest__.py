# -*- coding: utf-8 -*-
{
    'name': "Withholding Tree",
    'summary': "",
    'description': "",
    'author': "PP",
    'website': "",
    'category': 'Tree',
    'version': '12.0.01',
    'depends': ['base',
                'l10n_th_withholding_tax_report',
                'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/paper_format.xml',
        'data/report_data.xml',
        'report/templates/layouts.xml',
        'report/templates/report_withholding_tax_pdf.xml',
    ],
}