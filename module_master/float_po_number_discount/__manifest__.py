# -*- coding: utf-8 -*-
{
    'name': "Float PO discount for sale, bill, order & invoice lines",

    'summary': """
        Adds option to set float discount value for Purchase order.""",

    'description': """
        
    """,

    'author': "wattanadev",
    'website': "http://bione.co.th/",

    'category': 'Purchase',
    'version': '12.0.1.0.0',
    'license': 'LGPL-3',
    'support': '',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
