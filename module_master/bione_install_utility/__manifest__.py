# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Utility Library',
    'category': 'Generic Modules',
    'summary': 'Utility Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'all_in_one_cancel',
        'web_timeline',
        'base_view_inheritance_extension',
        'jt_sale_order_line_views',
        'sale_order_line_number',
        'account_invoice_line_number',
        'fiscal_year_sequence_extensible',
        'product_code_unique',
        'stock_inventory_cost_info',
        'product_cost_price_avco_sync',
        'purchase_stock_price_unit_sync',
        'stock_inventory_revaluation',
        'stock_picking_cancel_cs',
        'ki_po_line_sequence',
        'account_budget_oca',
        'analytic_tag_dimension',
        'web_widget_x2many_2d_matrix',


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
