# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Stock Picking (Delivery Order) & Reset to Draft',
    'version' : '1.0',
    'author':'wattanadev',
    'category': 'Stock',
    'maintainer': 'thaiodoo',
    'summary': """Enable auto cancel transfered delivery or cancel stock picking. Auto Cancel Delivery Order and Auto Cancel Receivable products.""",
    'website': '',
    'license': 'OPL-1',
    'support':'',
    'depends' : ['stock','account_cancel','sale_management','purchase','sale_stock'],
    'data': [
        'views/stock_picking.xml',
        'views/res_config_settings_views.xml',
        'views/view_sale_order.xml',
        'views/view_purchase_order.xml',
        'wizard/view_cancel_delivery_wizard.xml',

    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'], 
    'price': 14.99,
    'currency': 'EUR',
}
