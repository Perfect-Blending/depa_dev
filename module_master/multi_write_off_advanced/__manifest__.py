# -*- coding: utf-8 -*-


{
    'name': 'Multiple Write Off Lines in Register Payments(Advanced) - Writeoff',
    'version': '12.0.1.1',
    'category': 'Accounting',
    'sequence': 1,
    'summary': 'Multiple Write Off Lines in Register Payments',
    'description': """
Manage multiple write off in customer and supplier payments
===========================================================

This application allows you to add multiple write off into single/batch customer or supplier payments.

    """,
    'website': '',
    'author': 'wattanadev',
    'depends': ['account'],
    'price': 110,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'data': [
        'views/account_payment_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'css': [],
    'images': ['images/multi_writeoff_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
