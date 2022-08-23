# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Depa Fin Thai Account',
    'version': '12.0.1.0.0',
    'author': 'Thatsawan',
    'license': 'AGPL-3',
    'website': '',
    'category': 'account',
    'depends': [
                'bione_thai_account',
                'fin_system',
                ],
    'data': [
        'views/account_advance_request_view.xml',
    ],
    'installable': True,
}
