# -*- coding: utf-8 -*-
{
    'name': "FIN System",

    'summary': """
        Financial System""",

    'description': """
        FIN_100, FIN_401, FIN_201 including in this apps
    """,

    'author': "Zephyr",
    'website': "https://www.perfect.in.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'analytic',
        'uom',
        'product',
        'sale_management',
        'stock',
    ],

    # always loaded
    'data': [
        'data/fin_data.xml',
        'data/subsidized_measurement_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fin_system_view.xml',
        'views/analytic_account_view.xml',
        'views/fin_purchase_request_wiz.xml',
        'views/fin_100_view.xml',
        'views/fin_401_view.xml',
        'views/fin_201_view.xml',
        'views/fin_201_view_history.xml',
        'views/hr_view.xml',
	    'views/fin_100_request_wiz.xml',
        'views/fin_201_request_101_wiz.xml',
        'views/fw_pfb_fin_settings.xml',
        'views/fw_pfb_fin_settings2.xml',
        'views/fw_pfb_flow_template.xml',
        'views/fw_pfb_objective.xml',
        'views/fin_purchase_view.xml',
        'views/fin_100_view_history.xml',
        'views/purchase_request_view.xml',
        'report/fin_system_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
