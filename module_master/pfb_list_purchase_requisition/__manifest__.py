# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'List Purchase Requisition',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Fields',
    'depends': ['base',
                'web',
                'purchase',
                'purchase_requisition',
                ],


    'data': [
        'models/purchase_order.xml'

    ],
    'installable': True,
}
