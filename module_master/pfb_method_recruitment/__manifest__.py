# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'PFB Method Of Recruitment',
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
        'views/method_recruitment.xml',
        'views/purchase_order.xml',
        'views/job_position.xml',

    ],
    'installable': True,
}
