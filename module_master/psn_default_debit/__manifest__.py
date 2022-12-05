# -*- coding: utf-8 -*-

{
    'name': 'PSN  Default Debit',
    'version': '1.0',
    'author': 'wattan',
    'summary': 'Sort Journal Entry Lines by Debit',
    'description': """ Sort Journal Entry Lines by Debit """,
    'category': 'Accounting',
    'website': 'https://www.psn.co.th/',
    'license': 'AGPL-3',

    'depends': ['base', 'account',
                ],

    'data': [
        'views/account_move_view.xml',
    ],

    'qweb': [],
    'images': ['static/description/Debit-Banner.jpg'],

    'installable': True,
    'application': True,
    'auto_install': False,
}
