# -*- coding: utf-8 -*-
{
    'name': "Sale Report & Listviews",
    'summary': "",
    'description': "",
    'author': "PP",
    'website': "",
    'category': 'Report',
    'version': '12.0.01',
    'depends': ['base',
                'bione_thai_account',
                'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_report_wizard_view.xml',
        'views/purchase_views.xml',
        'views/sale_views.xml',

    ],
}
