# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Stock Library',
    'category': 'Generic Modules',
    'summary': 'Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'product_analytic',
        'stock_account_valuation_report',
        'stock_analysis',
        'stock_analytic',
        'stock_card_report',
        'stock_cycle_count',
        'stock_financial_risk',
        'stock_inventory_analytic',
        'stock_inventory_turnover_report',
        'stock_inventory_valuation_location',
        'stock_inventory_valuation_report',
        'stock_move_line_auto_fill',
        'stock_picking_invoice_link',
        'stock_picking_invoicing',
        'stock_split_picking',
        'bione_invoice_stock_move',
        'stock_request',
        'stock_request_analytic',
        'stock_request_kanban',
        'stock_request_purchase',
        'stock_request_submit',
        'stock_no_negative',
        'inventory_adjustment_cancel_app',
        'bi_inventory_adjustment_with_cost',
        'bione_picking_lot_expiry',
        # 'stock_force_date_app',
        # 'bi_inventory_valuation_fifo_report',
        'rt_stock_card',

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
