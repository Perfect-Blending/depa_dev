# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne STD01',
    'category': 'STD Modules',
    'summary': 'STD01 Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'bione_install_base',
        'bione_install_thai',
        'bione_install_purchase',
        'bione_install_sale',
        'bione_install_partner',
        'bione_install_hr',
        'bione_install_account',
        'bione_install_stock',
        'bione_install_tier_validation',
        'bione_install_report',
        'bione_install_utility',
        'bione_install_document',
        'bione_install_mrp',

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
