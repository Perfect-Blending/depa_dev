# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Journal Voucher Form Qweb',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'li cense': 'AGPL-3',
    'website': '',
    'category': 'Report',
    'depends': ['base',
                'web',
                ],


    'data': [
        'data/paper_format.xml',
        'reports/layout.xml',
        'data/report_data.xml',
    ],
    'installable': True,
}
