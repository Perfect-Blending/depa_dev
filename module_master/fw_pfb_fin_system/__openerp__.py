# -*- coding: utf-8 -*-
{
    'name': "FIN System",

    'summary': """
        FIN System
        """,

    'description': """
        FIN_100, FIN_401, FIN_201 including in this apps

    """,

    'author': "Zephyr",
    'website': "https://www.perfect.in.th",
    'category': 'Uncategorized',
    'version': '9.0.1',
    'depends': [
        'base',
        'hr',
        'product',
        'website_quote',
        'fw_pfb_budget_system',
        'fw_pfb_common_service',
        'fw_ksp_pr',
    ],

    # always loaded
    'data': [
        'data/fin_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fin_system_view.xml',
        'views/fin_100_view.xml',
        'views/fin_401_view.xml',
        'views/fin_201_view.xml',
        'views/hr_view.xml',
	    'views/fin_100_request_wiz.xml',
        'views/fin_201_request_101_wiz.xml',
        'views/fin_purchase_request_wiz.xml',
        'views/fw_pfb_fin_settings.xml',
        'views/fw_pfb_fin_settings2.xml',
        'views/fw_pfb_flow_template.xml',
        'views/fw_pfb_objective.xml',
        'views/fin_purchase_view.xml',
        'views/fin_100_view_history.xml',
        'report/fin_system_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
