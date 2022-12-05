# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Payment Order Type',
    'version': '12.0.1.0.0',
    'author': 'thaiodoo',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'purchase',
    ],
    'website': 'https://thaiodoo.com',
    'data': [
        'security/ir.model.access.csv',
        'views/view_payment_order_type.xml',
        'views/view_payment_order.xml',
        'views/res_partner_view.xml',
        'data/payment_order_type.xml',
    ],
    'installable': True,
    'auto_install': False,
}
