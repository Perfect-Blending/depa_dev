{
    'name': 'BiOne Purchase',
    'summary': 'Modify field in purchase module',
    'version': '12.0.1.0.0',
    'category': 'Purchases',
    'website': 'https://bione.co.th',
    'author': 'BiOne',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order_views.xml',
    ],
}
