# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'BiOne All In One Cancel Sales,Purchases and Delivery/Incoming Shipments, Invoice',
    'version' : '1.0',
    'author':'wattanadev',
    'category': 'Sales',
    'maintainer': 'BiOne',
    'summary': """ all in one cancel  ALL IN ONE CANCEL
    """,

    'website': '',
    'license': 'OPL-1',
    'support':'',
    'depends' : ['purchase_stock','account_cancel','sale_management','sale_stock'],
    'data': [

        'views/res_config_settings_views.xml',
        'views/view_purchase_order.xml',
        'views/stock_warehouse.xml',
        'views/view_sale_order.xml',
        'views/stock_picking.xml',
        'wizard/view_cancel_invoice_wizard.xml',
        'views/invoice.xml',
        'wizard/view_cancel_delivery_wizard.xml',

    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0,
    'currency': 'THB',
    'images': ['static/description/main_screen.png'],

}
