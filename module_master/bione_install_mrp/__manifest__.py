# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne MRP Library',
    'category': 'Generic Modules',
    'summary': 'MRP Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'account_move_line_manufacture_info',
        'antech_mrp_material_cost',
        'bi_odoo_process_costing_manufacturing',
        'mrp_analytic',
        'mrp_auto_assign',
        'mrp_bom_component_menu',
        'mrp_bom_current_stock',
        'mrp_bom_line_sequence',
        'mrp_bom_location',
        'mrp_bom_matrix_report',
        'mrp_bom_note',
        'mrp_bom_structure_report_level_1',
        'mrp_bom_structure_xlsx',
        'mrp_bom_structure_xlsx_level_1',
        'mrp_bom_tracking',
        'mrp_flattened_bom_xlsx',
        'mrp_multi_level',
        'mrp_multi_level_estimate',
        'mrp_planned_order_matrix',
        'mrp_production_auto_post_inventory',
        'mrp_production_grouped_by_product',
        'mrp_production_note',
        'mrp_production_putaway_strategy',
        'mrp_production_request',
        'mrp_sale_info',
        'mrp_stock_orderpoint_manual_procurement',
        'mrp_subcontracting',
        'mrp_unbuild_tracked_raw_material',
        'mrp_warehouse_calendar',
        # 'mrp_workcenter_capacity',
        # 'mrp_workcenter_costing',
        'mrp_workorder_sequence',
        'product_mrp_info',
        'product_quick_bom',
        'quality_control',
        'quality_control_issue',
        'quality_control_mrp',
        'quality_control_stock',
        'quality_control_team',
        'repair_calendar_view',
        'repair_discount',
        'repair_refurbish',
        'stock_picking_product_kit_helper',
        'unicoding_mrp_production_edit',
        'eq_cancel_mrp_orders',
        'jt_mrp_extra_componants',
        'antech_mrp_material_cost',
        'to_mrp_backdate',
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
