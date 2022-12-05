# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.

{
    'name' : 'FIN system Extension',
    'version' : '1.0',
    'summary': 'Customs Job',
    'sequence': 100,
    "author" : "ProThai Technology Co., Ltd.",
    'description': """
FIN Improvement
    - FIN 100
       |- FIN 401
       |- FIN 201
    - FIN to Purchase Order
    - fix budget computation
    - improve approval step
    - approval notification by email (10:00, 14:00)
    """,
    "category": "Uncategorized",
    "website" : "http://prothaitechnology.com",
    'depends' : [
        'purchase',
        'fin_system',
        'pfb_saraban',
    ],
    'data': [

        # data

        # wizard
        'wizard/wizard_fin100_approval_views.xml',
        'wizard/wizard_fin401_approval_views.xml',
        'wizard/wizard_fin201_approval_views.xml',
        'wizard/wizard_fin_purchase_approval_views.xml',
        'wizard/wizard_recompute_analytic_account.xml',

        # views
        "views/analytic_account_view.xml",
        "views/fin_100_views.xml",
        "views/fin_401_views.xml",
        "views/fin_201_views.xml",
        "views/approval_template_views.xml",
        "views/fin_purchase_views.xml",
        "views/fw_pfb_fin_settings2.xml",

        # printform

        # reports

        # access
        #'security/security.xml',
        #'security/ir.model.access.csv',

        # cron job
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '',
    "license": "Other proprietary",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
