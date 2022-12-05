{
    'name': 'Billing Order Type',
    'version': '12.0.1.0.0',
    'author': 'wattanadev',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'account_billing',
    ],
    'website': 'https://bionesoft.com',
    'data': [
        'security/ir.model.access.csv',
        'views/view_billing_order_type.xml',
        'views/view_billing_order.xml',
        'views/res_partner_view.xml',
        'data/billing_order_type.xml',
    ],
    'installable': True,
    'auto_install': False,
}
