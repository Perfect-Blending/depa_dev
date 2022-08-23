# -*- coding: utf-8 -*-
{
    'name': "depa_fin",

    'summary': """
        For inherit Fin module
        """,

    'description': """
        For inherit Fin module
    """,

    'author': "MIS - depa",
    'website': "http://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'fin_system'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_fin_views.xml',

        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}