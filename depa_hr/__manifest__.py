# -*- coding: utf-8 -*-
{
    'name': "depa_HR",

    'summary': """
        For depa's human resource management""",

    'description': """
        For depa's human resource management
    """,

    'author': "MIS - depa",
    'website': "https://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.1.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'fin_system',
    ],

    # always loaded
    'data': [
        'security/hr_group.xml',
        'security/ir.model.access.csv',
        'wizard/show_kpi_result_wizard.xml',
        'wizard/show_group_wizard.xml',
        'wizard/show_kpi_result_underline_wizard.xml',
        'views/kpi_main_view.xml',
        'views/kpi_round_setting_view.xml',
        'views/kpi_contribution_setting_view.xml',
        'views/kpi_behaviour_setting_view.xml',
        'views/kpi_setting_view.xml',
        'views/kpi_evaluate_setting_view.xml',
        'views/kpi_evaluate_view.xml',
        'views/hr_employee_view.xml',
        'wizard/make_kpi_evaluate_wizard.xml',
        'views/kpi_evaluated_all_view.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}