# -*- coding: utf-8 -*-

{
    'name': 'Odoo POS note and odoo pos product note, pos order note',
    'version': '12.0.0.0.0',
    'category': 'Point of Sale',
    'summary': 'Add pos order note and pos sale note add easily and supported in community and enterprise edition of odoo',
    'description': """
        Point of sale order note and product order note with easy step and support in community and enterprise of odoo.
    """,
    'depends': ['base', 'point_of_sale'],
    "data": [
        'views/point_of_sale.xml',
        'views/pos_note.xml',
        'views/pos_order_view_inherit.xml'
    ],
    'qweb': ['static/src/xml/pos.xml'],
    
    'application': True,
    'license': 'AGPL-3',
    'price': 10.00,
    'currency': 'USD',
    'support': 'www.yoursoft.co.th',
    'author': 'wattanadev',
    'website': 'http://www.yoursoft.co.th',
    'images': ['static/description/images/Banner-Img.png'],
}