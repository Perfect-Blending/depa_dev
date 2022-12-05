# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Budget Library',
    'category': 'Generic Modules',
    'summary': 'Budget Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'account_budget_oca',
        'analytic_tag_dimension',
        'web_widget_x2many_2d_matrix',
        # 'web_widget_x2many_2d_matrix_example',
        'budget_control',
        'budget_control_expense',
        'budget_control_expense_tag_dimension',
        'budget_control_purchase',
        'budget_control_purchase_request',
        'budget_control_purchase_tag_dimension',
        'budget_control_sale',
        'budget_control_tag_dimension',
        'budget_control_tier_validation',
        'budget_control_transfer',
        'account_budget_template',
        'budget_control_demo_full_cycle',


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
