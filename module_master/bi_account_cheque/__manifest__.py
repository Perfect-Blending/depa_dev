# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Cheque Life Cycle Management Odoo',
    'version': '12.0.1.0',
    'category': 'Accounting',
    'summary': 'Help of this app Manage complete of life cycle of Cheque Management System in Odoo',
    'description' :"""Account Cheque management
    Account Cheque Life Cycle Management Odoo
    

    """,
    'author': 'wattanadev',
    'website': '',
    'depends': ['account','base','sale_management'],
    'data': [
            'security/ir.model.access.csv',
            'security/account_cheque_security.xml',
            'report/account_cheque_report_view.xml',
            'report/account_cheque_report_template_view.xml',
            'views/account_cheque_view.xml',
            'views/res_config_settings.xml',
            
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "price": 89,
    "currency": "EUR",
    'live_test_url':'',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
