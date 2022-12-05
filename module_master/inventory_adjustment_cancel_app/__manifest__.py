# -*- coding: utf-8 -*-
{
    'name': 'Inventory Adjustment Cancel',
    "author": "wattanadev",
    'version': '12.0.1.2',
    'live_test_url': "https://www.bionesoft.com",
    "images":['static/description/main_screenshot.png'],
    'summary': "This app helps user to cancel inventory adjustment even if in validated state.",
    'description': """

""",
    "license" : "OPL-1",
    'depends': ['base','sale_management','stock','account','purchase','stock_account','account_cancel'],
    'data': [
            'views/inventory_views.xml',
            ],
    'installable': True,
    'auto_install': False,
    'price': 20,
    'currency': "THB",
    'category': 'Warehouse',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
