# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'All Qweb Form Depa',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Report',
    'depends': ['base',
                'web',
                'bione_thai_account',
                ],

    'data': [
        'data/paper_format.xml',
        'data/report_data.xml',
        'views/layout.xml',
        'views/cash_receipt.xml',
        'views/purchase_voucher.xml',
        'views/payment_voucher.xml',
        'views/wht.xml',
        'views/customer_receipts.xml',

    ],
    'installable': True,
}
