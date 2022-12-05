# -*- coding: utf-8 -*-

{
    'name' : "All in One Secondary Unit of Measure Sales, Purchase, Accounting and Inventory",
    "author": "wattanadev",
    'version': '12.0.1.2',
    'live_test_url': "",
    "images":['static/description/main_screenshot.png'],
    'summary': 'All in one secondary unit of measure Sales, Purchase, Accounting and Inventory.',
    'description' : '''
            All in one secondary unit of measure Sales, Purchase, Accounting and Inventory.
    
secondary uom
Stock in Different UOMs
uom
Unit of Measure
Account - Secondary Unit of Measure
Secondary Unit of measure
PRODUCT STOCK SECONDARY UOM QTY
STOCK SECONDARY UOM QTY
SECONDARY UOM QTY
UOM QTY
MRP-SECONDARY UOM
Manufacturing process with secondary UoM
Secondary UoM
Product Qty Secondary UoM
Qty Secondary UoM
Inventory - Secondary Unit of Measure
Inventory UoM
uom in invoice
uom in inventory
Multiple UoM for Single Product
Sales multi UOM
purchase SECONDARY UOM
Accounting uom
Multiple UOM
multi UOM
UOMS
second uoms
costing uom 
uom pricing 
uom costing
uom mRP
mrp uom
uom price 
UOM QTY
UOM QTY
PRODUCT UOM
stock uom


Pricing Based on Secondary UOM






    ''',
    "license" : "OPL-1",
    'depends' : ['sale_management','purchase','account','stock'],
    'data': [
            'security/secondary_uom_group.xml',
            'security/ir.model.access.csv',
            'views/product_view.xml',
            'views/sale_order_view.xml',
            'views/purchase_order_view.xml',
            'views/account_invoice_view.xml',
            'views/stock_move_view.xml',
            'views/stock_inventory_view.xml',
            'views/stock_quant_view.xml',
            'views/stock_scrap_view.xml',
            'views/delivery_report_template.xml',
            'views/invoice_report_template.xml',
            'views/purchase_report_template.xml',
            'views/sale_order_template.xml',
             ],
    'installable': True,
    'auto_install': False,
    'price': 18,
    'currency': "EUR",
    'category': 'Extra Tools',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
