# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo12 Accounting',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Accounting Reports',
    'sequence': '8',
    'author': 'wattanadev',
    'maintainer': 'thaiodoo',
    'support': 'wattana.bione@gmail.com',
    'website': '',
    'depends': ['accounting_pdf_reports'],
    'demo': [],
    'data': [
        'views/account.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}
