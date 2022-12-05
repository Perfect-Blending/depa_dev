# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

{
    'name': 'Copy Purchase Order Line',
    'category': 'Purchase',
    'version': '12.0.1.0',
    'sequence':5,
    'summary': "Plugin Will help to copy purchase order line. purchase Line Copy, copy line, copy, copy invoice line, sale, invoice, purchase",
    'description': "Plugin will help to copy purchase order line.",
    'author': 'OM Apps',
    'website': '',
    'depends': ['purchase'],
    'data': [
        'views/purchase_views.xml',
    ],
    'installable': True,
    'application': True,
    'images' : ['static/description/banner.png'],
    "price": 1.5,
    "currency": "EUR",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
