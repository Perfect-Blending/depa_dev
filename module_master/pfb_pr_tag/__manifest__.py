
{
    'name': 'Purchase Request Tag',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Fields',
    'depends': ['base',
                'web',
                'purchase_request',
                ],

    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request.xml',
    ],
    'installable': True,
}
