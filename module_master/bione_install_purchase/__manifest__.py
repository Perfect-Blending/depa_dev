# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Purchase Library',
    'category': 'Generic Modules',
    'summary': 'Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'purchase_analytic',
        'account_analytic_default_purchase',
        # 'purchase_backorder',
        'purchase_delivery_split_date',
        'purchase_deposit',
        'purchase_open_qty',
        'purchase_invoice_plan',
        'purchase_discount',
        'purchase_work_acceptance',
        'purchase_order_approved',
        'purchase_order_line_stock_available',
        'purchase_picking_state',
        'purchase_last_price_info',
        # 'purchase_order_type',
        'purchase_isolated_rfq',
        'product_form_purchase_link',
        'product_supplier_code_purchase',
        'purchase_product_usage',
        'purchase_request',
        'purchase_request_analytic',
        'purchase_request_department',
        'purchase_request_order_approved',
        'purchase_request_product_usage',
        'purchase_request_usage_department',
        'bione_purchase_req_add_approved_by_tree',

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
