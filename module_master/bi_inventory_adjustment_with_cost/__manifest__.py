# -*- coding: utf-8 -*-


{
    "name" : "Inventory Adjustment with Cost Price Odoo",
    "version" : "12.0.0.3",
    "category" : "Warehouse",
    'summary': 'Inventory Adjustment Cost Price Inventory Adjustment costing Inventory Adjustment',
    "description": """
    
    Inventory Adjustment with Cost

    Inventory adjustment with cost in odoo,
    set up cost price in inventory adjustment,
    generate journal entry from stock move in odoo,
    configured inventory adjustment with cost in odoo,
    

    
    """,
    "author": "wattanadev",
    "website" : "www.bione.co.th",
    "price": 29,
    "currency": 'THB',
    "depends" : ['base','account','stock','stock_account'],
    "data": [
        'views/setting.xml',
        'views/inventory.xml',
    ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
