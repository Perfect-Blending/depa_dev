# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2020 BiOne
#
##############################################################################
{
    'name': "BiOne Lot Expiry Date",
    'category': 'Stock',
    'version': '12.0.1.0',
    'author': 'wattanadev',
    'description': """
        This module allows user to enter lot expiry date in picking form.
        * Allows user to enter lot expiry dates in picking form while receive incoming shipment.
        * It works with lot/serial tracking product.
        * Calculated lot/serial dates automatically if product have dates configuration.
    """,
    'summary': """ This module allows user to enter lot expiry date in picking form. | Manual Lot Expiry date. | Expiry on Incoming Shipment. | Incoming Shipment Lot dates. | Purchase Lot dates | Expiry Date.""",
    'depends': ['product_expiry'],
    'price': 20,
    'currency': 'THB',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'views/stock_move_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
