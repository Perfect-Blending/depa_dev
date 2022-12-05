# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'PFB Purchase Requisition Field',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Fields',
    'depends': ['base',
                'web',
                'purchase_requisition',
                ],


    'data': [
        'security/ir.model.access.csv',
        'models/purchase_agreements_fields.xml',
    ],
    'installable': True,
}
