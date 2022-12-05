# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Invoice Plan Amount',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Fields',
    'depends': ['base',
                'web',
                'purchase_invoice_plan',
                'purchase',
                'purchase_work_acceptance',
                ],


    'data': [
        'views/purchase_invoice_plan.xml'

    ],
    'installable': True,
}
