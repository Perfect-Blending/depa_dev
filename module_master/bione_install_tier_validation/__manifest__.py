# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Tier Library',
    'category': 'Generic Modules',
    'summary': 'Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'purchase_tier_validation',
        'purchase_request_tier_validation',
        'hr_expense_tier_validation',
        'stock_request_tier_validation',

                ],
    'data': [
        # 'views/bo_ir_seq.xml',
    ],
    'installable': True,
    "active": False,
    "description": """

BiOne Library modules
====================================

Contain libary shared for BiOne modules

Change logs:
------------------------------------

* 2020-01-05(1) BO add running seq

""",
}
